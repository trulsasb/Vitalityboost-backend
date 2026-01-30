from models.payment import Payment, PaymentEvent, PaymentProvider, PaymentStatus
from database import SessionLocal
from datetime import datetime


class PaymentEngine:
    def __init__(self):
        self.db = SessionLocal()

    def create_payment(self, order, provider: PaymentProvider):
        payment = Payment(
            order_id=order.id,
            provider=provider,
            status=PaymentStatus.INITIATED,
            amount=order.total_amount,
            currency="NOK",
            created_at=datetime.utcnow(),
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def add_event(self, payment_id: int, event_type: str, raw_data: str = None):
        event = PaymentEvent(
            payment_id=payment_id,
            event_type=event_type,
            raw_data=raw_data,
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_status(self, payment_id: int, new_status: PaymentStatus):
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return None

        payment.status = new_status
        self.db.commit()
        self.db.refresh(payment)
        return payment
