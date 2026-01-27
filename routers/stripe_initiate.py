from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order
from models.payment import PaymentProvider, Payment
from payments.engine import PaymentEngine

router = APIRouter(prefix="/payments/stripe", tags=["stripe-initiate"])


def get_engine() -> PaymentEngine:
    """
    Temporary dependency until we wire up PaymentEngine in main.py.
    """
    from main import payment_engine
    return payment_engine


@router.post("/initiate")
def initiate_stripe_payment(order_id: int, db: Session = Depends(get_db), engine: PaymentEngine = Depends(get_engine)):
    # Fetch order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Create payment record
    payment = Payment(
        order_id=order.id,
        provider=PaymentProvider.STRIPE,
        amount=order.total_amount,
        currency=order.currency,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Initiate Stripe payment (placeholder)
    result = engine.initiate_payment(
        provider=PaymentProvider.STRIPE,
        order=order,
        return_url="https://vitalityboost.no/checkout/complete"  # adjust later
    )

    return {
        "redirect_url": result["redirect_url"],
        "payment_id": payment.id,
        "order_id": order.id,
    }
