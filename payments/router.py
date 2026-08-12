import httpx
import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order
from models.payment import Payment
from payments.vipps_auth import VippsAuth
from utils.env import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


# ---------------------------------------------------------
# STRIPE INITIATE PAYMENT
# ---------------------------------------------------------

@router.post("/stripe/initiate/{order_id}")
def initiate_stripe_payment(order_id: int, db: Session = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe is not configured (missing STRIPE_SECRET_KEY)")
    stripe.api_key = settings.STRIPE_SECRET_KEY

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = Payment(order_id=order.id, provider="stripe", status="pending", amount=order.total_amount, currency="NOK")
    db.add(payment)
    db.commit()
    db.refresh(payment)

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "nok",
                    "product_data": {"name": f"Vitalityboost order #{order.id}"},
                    "unit_amount": int(round(order.total_amount * 100)),
                },
                "quantity": 1,
            }],
            success_url=f"{settings.FRONTEND_URL}/checkout/success?order_id={order.id}",
            cancel_url=f"{settings.FRONTEND_URL}/checkout/cancel?order_id={order.id}",
            metadata={"order_id": str(order.id), "payment_id": str(payment.id)},
        )
    except Exception as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Stripe error: {e}")

    payment.external_reference = session.id
    db.commit()

    return {"payment_id": payment.id, "checkout_url": session.url}


# ---------------------------------------------------------
# VIPPS INITIATE PAYMENT
# ---------------------------------------------------------

@router.post("/vipps/initiate/{order_id}")
def initiate_vipps_payment(order_id: int, db: Session = Depends(get_db)):
    required = [settings.VIPPS_CLIENT_ID, settings.VIPPS_CLIENT_SECRET, settings.VIPPS_SUBSCRIPTION_KEY, settings.VIPPS_MSN]
    if not all(required):
        raise HTTPException(status_code=503, detail="Vipps is not configured (missing client id/secret/subscription key/MSN)")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = Payment(order_id=order.id, provider="vipps", status="pending", amount=order.total_amount, currency="NOK")
    db.add(payment)
    db.commit()
    db.refresh(payment)

    auth = VippsAuth(
        client_id=settings.VIPPS_CLIENT_ID,
        client_secret=settings.VIPPS_CLIENT_SECRET,
        subscription_key=settings.VIPPS_SUBSCRIPTION_KEY,
        base_url=settings.VIPPS_BASE_URL,
    )
    reference = f"vb-order-{order.id}-{payment.id}"

    try:
        headers = auth.get_headers()
        headers["Merchant-Serial-Number"] = settings.VIPPS_MSN
        body = {
            "amount": {"currency": "NOK", "value": int(round(order.total_amount * 100))},
            "paymentMethod": {"type": "WALLET"},
            "reference": reference,
            "returnUrl": f"{settings.FRONTEND_URL}/checkout/complete?order_id={order.id}",
            "userFlow": "WEB_REDIRECT",
            "paymentDescription": f"Vitalityboost order #{order.id}",
        }
        with httpx.Client(timeout=15) as client:
            resp = client.post(f"{settings.VIPPS_BASE_URL}/epayment/v1/payments", headers=headers, json=body)
        if resp.status_code >= 400:
            raise Exception(resp.text)
        data = resp.json()
    except Exception as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Vipps error: {e}")

    payment.external_reference = reference
    db.commit()

    return {"payment_id": payment.id, "checkout_url": data.get("redirectUrl")}


# ---------------------------------------------------------
# PAYMENT STATUS (frontend polling)
# ---------------------------------------------------------

@router.get("/{payment_id}/status")
def get_payment_status(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"payment_id": payment.id, "status": payment.status}
