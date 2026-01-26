from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# -----------------------------
#   PRODUCT
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


# -----------------------------
#   CART ITEM
# -----------------------------
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    session_id = Column(String(100), index=True, nullable=False)

    product = relationship("Product", back_populates="cart_items")


# -----------------------------
#   ORDER
# -----------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="pending")
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=True)
    customer_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# -----------------------------
#   ORDER ITEM
# -----------------------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# -----------------------------
#   USER (ADMIN)
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# -----------------------------
#   ACCOUNTING INTEGRATION
# -----------------------------
class AccountingIntegration(Base):
    __tablename__ = "accounting_integrations"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)  # 'tripletex' / 'fiken'
    api_key = Column(String(255), nullable=True)
    active = Column(Boolean, default=False)
    test_mode = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)

    # Viktig: default=dict (ikke {})
    config = Column(JSON, nullable=True, default=dict)
