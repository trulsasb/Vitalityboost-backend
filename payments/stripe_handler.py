from sqlalchemy.orm import Session
from database import SessionLocal
from models.payment import Payment
from models.payment_event import PaymentEvent


class StripeHandler:
    def initiate_payment(self, order_id: int, amount: float):
        db: Session = SessionLocal()

        payment = Payment(
            order_id=order_id,
            provider="stripe",
            status="initiated",
            amount=amount,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        event = PaymentEvent(
            payment_id=payment.id,
            event_type="initiated",
            data=f"Stripe payment initiated for order {order_id}",
        )
        db.add(event)
        db.commit()

        db.close()

        return {
            "payment_id": payment.id,
            "redirect_url": f"https://stripe.com/checkout/{payment.id}",
        }
