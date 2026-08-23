import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderStatus
from models.payment import Payment
from models.payment_event import PaymentEvent
from services.order_service import release_failed_order
from utils.env import settings
from utils.integration_settings import resolve_setting

router = APIRouter(prefix="/webhooks/stripe", tags=["Webhooks"])


@router.post("/")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    webhook_secret = resolve_setting(db, "stripe", "webhook_secret", settings.STRIPE_WEBHOOK_SECRET)
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook secret not configured")

    raw_body = await request.body()
    signature = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(raw_body, signature, webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    event_type = event["type"]
    obj = event["data"]["object"]
    reference = obj.get("id")

    payment = db.query(Payment).filter(Payment.external_reference == reference).first()
    if not payment:
        # Unrelated event, or one we don't track. Ack so Stripe stops retrying.
        return {"status": "ignored"}

    db.add(PaymentEvent(payment_id=payment.id, event_type=f"stripe_{event_type}", data=str(reference)))

    if event_type == "checkout.session.completed":
        payment.status = "completed"
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if order:
            order.status = OrderStatus.PAID
    elif event_type in ("checkout.session.expired", "payment_intent.payment_failed"):
        payment.status = "failed"
        release_failed_order(db, payment.order_id)

    db.commit()
    return {"status": "ok"}
