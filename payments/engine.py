from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol
from datetime import datetime

from models.payment import PaymentProvider, PaymentStatus
from models.payment_event import PaymentEventType
from models.order import OrderStatus
from models.payment import Payment
from models.payment_event import PaymentEvent
from models.order import Order


class PaymentHandler(Protocol):
    def initiate(self, order_id: int, amount: int, currency: str, return_url: str) -> Dict[str, Any]:
        ...

    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str]) -> Dict[str, Any]:
        ...


@dataclass
class PaymentEventData:
    event_type: PaymentEventType
    provider: PaymentProvider
    order_id: int
    payment_id: int
    amount: int
    currency: str
    raw_payload: Dict[str, Any]
    created_at: datetime


class PaymentEngine:
    def __init__(self, handlers: Dict[PaymentProvider, PaymentHandler], db_session_factory):
        self.handlers = handlers
        self.db_session_factory = db_session_factory

    def initiate_payment(self, provider: PaymentProvider, order, return_url: str):
        handler = self.handlers[provider]
        return handler.initiate(order.id, order.total_amount, order.currency, return_url)

    def process_webhook(self, provider: PaymentProvider, payload: Dict[str, Any], signature: Optional[str]):
        handler = self.handlers[provider]
        event_data = handler.handle_webhook(payload, signature)

        with self.db_session_factory() as db:
            payment = db.query(Payment).filter(Payment.id == event_data["payment_id"]).first()
            order = db.query(Order).filter(Order.id == event_data["order_id"]).first()

            # Create event
            evt = PaymentEvent(
                payment_id=payment.id,
                event_type=event_data["event_type"],
                raw_payload=event_data["raw_payload"],
            )
            db.add(evt)

            # Update payment status
            payment.status = event_data["event_type"].value.replace("payment_", "")

            # Update order status
            if event_data["event_type"] == PaymentEventType.CAPTURED:
                order.status = OrderStatus.PAID
            elif event_data["event_type"] == PaymentEventType.FAILED:
                order.status = OrderStatus.FAILED
            elif event_data["event_type"] == PaymentEventType.REFUNDED:
                order.status = OrderStatus.REFUNDED

            db.commit()

        return event_data
