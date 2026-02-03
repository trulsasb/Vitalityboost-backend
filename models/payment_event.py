from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    event_type = Column(String, nullable=False)
    data = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", back_populates="events")
