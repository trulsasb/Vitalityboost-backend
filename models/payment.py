from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from models import Base


class PaymentProvider(str, PyEnum):
    VIPPS = "vipps"
    STRIPE = "stripe"


class PaymentStatus(str, PyEnum):
    INITIATED = "initiated"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    provider = Column(Enum(PaymentProvider))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.INITIATED)
    amount = Column(Integer)  # i øre
    currency = Column(String, default="NOK")
    provider_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    order = relationship("Order", back_populates="payments")
    events = relationship("PaymentEvent", back_populates="payment")
