from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    session_id = Column(String(100), index=True, nullable=False)

    product = relationship("Product", back_populates="cart_items")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountingIntegration(Base):
    __tablename__ = "accounting_integrations"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)
    api_key = Column(String(255), nullable=True)
    active = Column(Boolean, default=False)
    test_mode = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)

    config = Column(JSON, nullable=True, default=dict)
