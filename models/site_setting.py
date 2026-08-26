from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from models.base import Base


class SiteSetting(Base):
    """Generic plain-text key/value store for small admin-editable settings
    that aren't secrets (e.g. which email address the contact form notifies).
    Unlike IntegrationSetting, values here are stored unencrypted -- don't
    put API keys or credentials in this table."""

    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
