from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from models import Base


class PaymentEventType(str, PyEnum):
    INITIATED = "payment_initiated"
    AUTHORIZED = "payment_authorized"
    CAPTURED = "payment_captured"
    FAILED = "payment_failed"
    REFUNDED = "payment_refunded"


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    event_type = Column(Enum(PaymentEventType))
    raw_payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", back_populates="events")
