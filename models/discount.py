from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_type = Column(String, nullable=False)  # "percentage" | "fixed"
    value = Column(Float, nullable=False)

    # Scope restrictions — null means "no restriction" (any customer / any
    # product). There's no Customer table yet, only an email string per
    # order, so customer scoping matches on email rather than an id.
    customer_email = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    active = Column(Boolean, nullable=False, default=True, server_default="true")
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, nullable=False, default=0, server_default="0")

    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", lazy="joined")


class DiscountRedemption(Base):
    """Audit trail of a code being applied to an order — kept as its own
    table (rather than columns on Order) so no existing table needs an
    ALTER TABLE; this one is simply new and auto-creates on deploy."""

    __tablename__ = "discount_redemptions"

    id = Column(Integer, primary_key=True, index=True)
    discount_code_id = Column(Integer, ForeignKey("discount_codes.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    discount_code = relationship("DiscountCode", lazy="joined")
