import secrets

import httpx
import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderStatus
from models.payment import Payment
from payments.vipps_auth import VippsAuth
from utils.env import settings
from utils.integration_settings import resolve_setting

router = APIRouter(prefix="/payments", tags=["Payments"])


# ---------------------------------------------------------
# STRIPE INITIATE PAYMENT
# ---------------------------------------------------------

@router.post("/stripe/initiate/{order_id}")
def initiate_stripe_payment(order_id: int, db: Session = Depends(get_db)):
    stripe_secret_key = resolve_setting(db, "stripe", "secret_key", settings.STRIPE_SECRET_KEY)
    if not stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured (missing secret key)")
    stripe.api_key = stripe_secret_key

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=409, detail="Order is not awaiting payment")

    payment = Payment(
        order_id=order.id,
        provider="stripe",
        status="pending",
        amount=order.total_amount,
        currency="NOK",
        status_token=secrets.token_urlsafe(24),
    )
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

    return {"payment_id": payment.id, "checkout_url": session.url, "status_token": payment.status_token}


# ---------------------------------------------------------
# VIPPS INITIATE PAYMENT
# ---------------------------------------------------------

@router.post("/vipps/initiate/{order_id}")
def initiate_vipps_payment(order_id: int, db: Session = Depends(get_db)):
    vipps_client_id = resolve_setting(db, "vipps", "client_id", settings.VIPPS_CLIENT_ID)
    vipps_client_secret = resolve_setting(db, "vipps", "client_secret", settings.VIPPS_CLIENT_SECRET)
    vipps_subscription_key = resolve_setting(db, "vipps", "subscription_key", settings.VIPPS_SUBSCRIPTION_KEY)
    vipps_msn = resolve_setting(db, "vipps", "msn", settings.VIPPS_MSN)
    vipps_base_url = resolve_setting(db, "vipps", "base_url", settings.VIPPS_BASE_URL)

    if not all([vipps_client_id, vipps_client_secret, vipps_subscription_key, vipps_msn]):
        raise HTTPException(status_code=503, detail="Vipps is not configured (missing client id/secret/subscription key/MSN)")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=409, detail="Order is not awaiting payment")

    payment = Payment(
        order_id=order.id,
        provider="vipps",
        status="pending",
        amount=order.total_amount,
        currency="NOK",
        status_token=secrets.token_urlsafe(24),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    auth = VippsAuth(
        client_id=vipps_client_id,
        client_secret=vipps_client_secret,
        subscription_key=vipps_subscription_key,
        base_url=vipps_base_url,
    )
    reference = f"vb-order-{order.id}-{payment.id}"

    try:
        headers = auth.get_headers()
        headers["Merchant-Serial-Number"] = vipps_msn
        body = {
            "amount": {"currency": "NOK", "value": int(round(order.total_amount * 100))},
            "paymentMethod": {"type": "WALLET"},
            "reference": reference,
            "returnUrl": f"{settings.FRONTEND_URL}/checkout/complete?order_id={order.id}",
            "userFlow": "WEB_REDIRECT",
            "paymentDescription": f"Vitalityboost order #{order.id}",
        }
        with httpx.Client(timeout=15) as client:
            resp = client.post(f"{vipps_base_url}/epayment/v1/payments", headers=headers, json=body)
        if resp.status_code >= 400:
            raise Exception(resp.text)
        data = resp.json()
    except Exception as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Vipps error: {e}")

    payment.external_reference = reference
    db.commit()

    return {"payment_id": payment.id, "checkout_url": data.get("redirectUrl"), "status_token": payment.status_token}


# ---------------------------------------------------------
# PAYMENT STATUS (frontend polling)
# ---------------------------------------------------------

@router.get("/{payment_id}/status")
def get_payment_status(payment_id: int, token: str | None = None, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # payment_id alone is a sequential int anyone could enumerate to read
    # other customers' payment statuses. status_token closes that, but is
    # only enforced once a token was actually issued for this payment (rows
    # created before this field existed, or a caller not passing it yet
    # during frontend rollout, fall back to the old behavior) and only
    # rejected on an explicit mismatch -- never silently ignored.
    if payment.status_token and token is not None and not secrets.compare_digest(token, payment.status_token):
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"payment_id": payment.id, "status": payment.status}
