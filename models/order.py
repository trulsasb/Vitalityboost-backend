from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_primary=True, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")

    payments = relationship("Payment", backref="order")
