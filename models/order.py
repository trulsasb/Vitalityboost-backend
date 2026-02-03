from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional link to user (no FK, no migration)
    user_id = Column(Integer, nullable=True)

    # Relationship to order items
    items = relationship(
        "OrderItem",
        back_populates="order",
        lazy="joined",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Back reference to order
    order = relationship(
        "Order",
        back_populates="items",
        lazy="joined",
    )
