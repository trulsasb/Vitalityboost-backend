from sqlalchemy.orm import Session

from models.payment import Payment, PaymentProvider, PaymentStatus
from models.payment_event import PaymentEvent


class PaymentEngine:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # CREATE PAYMENT
    # ---------------------------------------------------------

    def create_payment(self, order_id: int, provider: str, amount: float):
        payment = Payment(
            order_id=order_id,
            provider=provider,
            status=PaymentStatus.PENDING,
            amount=amount,
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    # ---------------------------------------------------------
    # UPDATE PAYMENT STATUS
    # ---------------------------------------------------------

    def update_status(self, payment_id: int, new_status: str):
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return None

        payment.status = new_status
        self.db.commit()
        self.db.refresh(payment)
        return payment

    # ---------------------------------------------------------
    # ADD PAYMENT EVENT
    # ---------------------------------------------------------

    def add_event(self, payment_id: int, event_type: str, data: dict):
        event = PaymentEvent(
            payment_id=payment_id,
            event_type=event_type,
            data=data,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
