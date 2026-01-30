from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    events = relationship("PaymentEvent", back_populates="payment")
