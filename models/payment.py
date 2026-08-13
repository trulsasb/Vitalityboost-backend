from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # "stripe" eller "vipps"
    provider = Column(String, nullable=False)

    # f.eks. "pending", "completed", "failed"
    status = Column(String, nullable=False, default="pending")

    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="NOK")

    # Provider's reference for this payment (Stripe Checkout Session id,
    # Vipps orderId, etc.) — used to match incoming webhooks back to a row.
    external_reference = Column(String, nullable=True, index=True)

    # Relationship to payment events
    events = relationship(
        "PaymentEvent",
        back_populates="payment",
        lazy="joined",
        cascade="all, delete-orphan",
    )

