from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from payments.stripe_handler import StripeHandler
from payments.vipps_handler import VippsHandler
from payments.engine import PaymentEngine
from models.payment import Payment, PaymentEvent

router = APIRouter(prefix="/payments", tags=["Payments"])


# -----------------------------
# INITIATE PAYMENTS
# -----------------------------

@router.post("/stripe/initiate")
def initiate_stripe_payment(order_id: int, amount: float, db: Session = Depends(get_db)):
    handler = StripeHandler()
    return handler.initiate_payment(order_id=order_id, amount=amount)


@router.post("/vipps/initiate")
def initiate_vipps_payment(order_id: int, db: Session = Depends(get_db)):
    handler = VippsHandler()
    return handler.initiate_payment(order_id=order_id)


# -----------------------------
# PAYMENT LOOKUP / ADMIN
# -----------------------------

@router.get("/")
def list_payments(db: Session = Depends(get_db)):
    return db.query(Payment).order_by(Payment.id.desc()).all()


@router.get("/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/{payment_id}/events")
def get_payment_events(payment_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(PaymentEvent)
        .filter(PaymentEvent.payment_id == payment_id)
        .order_by(PaymentEvent.timestamp.desc())

