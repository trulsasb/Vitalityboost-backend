from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from datetime import datetime
from enum import Enum as PyEnum
from models import Base


class OrderStatus(str, PyEnum):
    PENDING_PAYMENT = "pending_payment"
    AUTHORIZED = "authorized"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    total_amount = Column(Integer)  # i øre
    currency = Column(String, default="NOK")
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT)
    created_at = Column(DateTime, default=datetime.utcnow)

    # cart snapshot
    items = Column(JSON)
