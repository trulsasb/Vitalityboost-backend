from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False, server_default="false")

    # Granular admin-panel permissions for non-owner staff accounts.
    # is_admin (above) is the owner level and implies all of these.
    can_view_products = Column(Boolean, nullable=False, default=False, server_default="false")
    can_edit_products = Column(Boolean, nullable=False, default=False, server_default="false")
    can_view_orders = Column(Boolean, nullable=False, default=False, server_default="false")
    can_view_payments = Column(Boolean, nullable=False, default=False, server_default="false")
    can_manage_accounting = Column(Boolean, nullable=False, default=False, server_default="false")

    created_at = Column(DateTime, server_default=func.now())

