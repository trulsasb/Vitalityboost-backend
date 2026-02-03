from models.payment import Payment
from models.payment_event import PaymentEvent
from database import SessionLocal


class StripeHandler:
    """
    Mock Stripe handler.
    """

    def initiate_payment(self, order_id: int):
        db = SessionLocal()

        payment = Payment(
            order_id=order_id,
            provider="stripe",
            status="pending",
            amount=100.0,  # mock amount
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        event = PaymentEvent(
            payment_id=payment.id,
            event_type="stripe_initiated",
            data="Stripe payment initiated",
        )
        db.add(event)
        db.commit()

        return {"payment_id": payment.id, "status": "pending"}

    def confirm_payment(self, payment_id: int):
        db = SessionLocal()

        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment or payment.provider != "stripe":
            raise Exception("Stripe payment not found")

        payment.status = "completed"
        db.commit()

        event = PaymentEvent(
            payment_id=payment.id,
            event_type="stripe_confirmed",
            data="Stripe payment confirmed",
        )
        db.add(event)
        db.commit()

        return {"payment_id": payment.id, "status": "completed"}
