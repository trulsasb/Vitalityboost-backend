from models.payment import Payment
from models.payment_event import PaymentEvent
from database import SessionLocal


class VippsHandler:
    """
    Mock Vipps handler.
    """

    def initiate_payment(self, order_id: int):
        db = SessionLocal()

        payment = Payment(
            order_id=order_id,
            provider="vipps",
            status="pending",
            amount=100.0,  # mock amount
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        event = PaymentEvent(
            payment_id=payment.id,
            event_type="vipps_initiated",
            data="Vipps payment initiated",
        )
        db.add(event)
        db.commit()

        return {"payment_id": payment.id, "status": "pending"}

    def confirm_payment(self, payment_id: int):
        db = SessionLocal()

        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment or payment.provider != "vipps":
            raise Exception("Vipps payment not found")

        payment.status = "completed"
        db.commit()

        event = PaymentEvent(
            payment_id=payment.id,
            event_type="vipps_confirmed",
            data="Vipps payment confirmed",
        )
        db.add(event)
        db.commit()

        return {"payment_id": payment.id, "status": "completed"}
