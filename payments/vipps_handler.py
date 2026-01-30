import os
import requests
from database import SessionLocal
from models.payment import Payment, PaymentEvent, PaymentProvider, PaymentStatus
from datetime import datetime


class VippsHandler:
    def __init__(self):
        self.db = SessionLocal()
        self.client_id = os.getenv("VIPPS_CLIENT_ID")
        self.client_secret = os.getenv("VIPPS_CLIENT_SECRET")
        self.subscription_key = os.getenv("VIPPS_SUBSCRIPTION_KEY")
        self.merchant_serial_number = os.getenv("VIPPS_MSN")
        self.base_url = os.getenv("VIPPS_BASE_URL")

    def initiate_payment(self, order):
        payment = Payment(
            order_id=order.id,
            provider=PaymentProvider.VIPPS,
            status=PaymentStatus.INITIATED,
            amount=order.total_amount,
            currency="NOK",
            created_at=datetime.utcnow(),
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        self._log_event(payment.id, "initiated")

        return {
            "payment_id": payment.id,
            "redirect_url": f"https://vipps.no/checkout/{payment.id}"
        }

    def _log_event(self, payment_id: int, event_type: str, raw_data: str = None):
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
