import base64
import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderStatus
from models.payment import Payment
from models.payment_event import PaymentEvent
from utils.env import settings
from utils.integration_settings import resolve_setting

router = APIRouter(prefix="/webhooks/vipps", tags=["Webhooks"])

# Vipps ePayment API event names that mean "money has moved / is confirmed"
_SUCCESS_EVENTS = {"AUTHORIZED", "CAPTURED"}
_FAILURE_EVENTS = {"CANCELLED", "EXPIRED", "TERMINATED", "FAILED"}

_EXPECTED_SIGNED_HEADERS = "x-ms-date;host;x-ms-content-sha256"


def _verify_signature(request: Request, raw_body: bytes, webhook_secret: str) -> None:
    """Verify Vipps's HMAC-SHA256 webhook signature.

    Scheme: https://developer.vippsmobilepay.com/docs/APIs/webhooks-api/request-authentication/
    The secret is the one returned when the webhook was registered via POST /webhooks.
    """

    date_header = request.headers.get("x-ms-date")
    content_hash_header = request.headers.get("x-ms-content-sha256")
    authorization = request.headers.get("authorization")
    host = request.headers.get("host")

    if not all([date_header, content_hash_header, authorization, host]):
        raise HTTPException(status_code=401, detail="Missing webhook authentication headers")

    expected_content_hash = base64.b64encode(hashlib.sha256(raw_body).digest()).decode()
    if not hmac.compare_digest(expected_content_hash, content_hash_header):
        raise HTTPException(status_code=401, detail="Webhook content hash mismatch")

    try:
        scheme, rest = authorization.split(" ", 1)
        params = dict(p.split("=", 1) for p in rest.split("&"))
        signed_headers = params["SignedHeaders"]
        signature = params["Signature"]
    except Exception:
        raise HTTPException(status_code=401, detail="Malformed Authorization header")

    if scheme != "HMAC-SHA256" or signed_headers != _EXPECTED_SIGNED_HEADERS:
        raise HTTPException(status_code=401, detail="Unexpected Authorization header format")

    path_and_query = request.url.path
    if request.url.query:
        path_and_query += f"?{request.url.query}"

    string_to_sign = f"POST\n{path_and_query}\n{date_header};{host};{content_hash_header}"
    expected_signature = base64.b64encode(
        hmac.new(webhook_secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    ).decode()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@router.post("/")
async def vipps_webhook(request: Request, db: Session = Depends(get_db)):
    webhook_secret = resolve_setting(db, "vipps", "webhook_secret", settings.VIPPS_WEBHOOK_SECRET)
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Vipps webhook secret not configured")

    raw_body = await request.body()
    _verify_signature(request, raw_body, webhook_secret)
    payload = json.loads(raw_body)

    reference = payload.get("reference")
    event_name = payload.get("name") or payload.get("eventName") or "unknown"

    if not reference:
        return {"status": "ignored", "reason": "no reference in payload"}

    payment = db.query(Payment).filter(Payment.external_reference == reference).first()
    if not payment:
        return {"status": "ignored", "reason": "unknown reference"}

    db.add(PaymentEvent(payment_id=payment.id, event_type=f"vipps_{event_name}", data=str(payload)))

    if event_name in _SUCCESS_EVENTS:
        payment.status = "completed"
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if order:
            order.status = OrderStatus.PAID
    elif event_name in _FAILURE_EVENTS:
        payment.status = "failed"

    db.commit()
    return {"status": "ok"}
