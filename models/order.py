from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from database import Base


class OrderStatus(str, PyEnum):
    PENDING_PAYMENT = "pending_payment"
    AUTHORIZED = "authorized"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # session_id fjernet for å matche eksisterende database
    total_amount = Column(Integer)
    currency = Column(String, default="NOK")
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments = relationship(
        "Payment",
        back_populates="order",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
