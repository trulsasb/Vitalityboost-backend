from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderStatus
from models.payment import Payment
from models.payment_event import PaymentEvent

router = APIRouter(prefix="/webhooks/vipps", tags=["Webhooks"])

# Vipps ePayment API event names that mean "money has moved / is confirmed"
_SUCCESS_EVENTS = {"AUTHORIZED", "CAPTURED"}
_FAILURE_EVENTS = {"CANCELLED", "EXPIRED", "TERMINATED", "FAILED"}


@router.post("/")
async def vipps_webhook(request: Request, db: Session = Depends(get_db)):
    # NOTE: Vipps's ePayment webhooks are authenticated via a callback token
    # you configure per-webhook in the Vipps portal, sent back as an
    # Authorization header. Compare it against your configured value here
    # once you've registered the webhook in the Vipps merchant portal —
    # the exact header name/value is only visible after you set it up there,
    # so this is left as a clearly-marked TODO rather than guessed at.
    payload = await request.json()

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
