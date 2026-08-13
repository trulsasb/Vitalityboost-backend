import enum
from sqlalchemy import Column, Enum, Float, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False, default=0)
    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING_PAYMENT,
        server_default=OrderStatus.PENDING_PAYMENT.value,
    )

    # Optional link to user (no FK)
    user_id = Column(Integer, nullable=True)

    # Shipping/contact details, required for physical delivery. Nullable at
    # the DB level so this doesn't break rows that predate this column; the
    # /orders/direct endpoint enforces them as required on new orders.
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    shipping_address = Column(String, nullable=True)
    shipping_zip = Column(String, nullable=True)
    shipping_city = Column(String, nullable=True)

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
    price_at_purchase = Column(Float, nullable=False, default=0)

    order = relationship(
        "Order",
        back_populates="items",
        lazy="joined",
    )
