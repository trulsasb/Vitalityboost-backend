from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from models.base import Base


class IntegrationSetting(Base):
    """Encrypted-at-rest credentials for third-party integrations (Stripe,
    Vipps, and eventually Tripletex/Fiken) entered via the admin dashboard,
    instead of only being settable as Render environment variables."""

    __tablename__ = "integration_settings"
    __table_args__ = (UniqueConstraint("provider", "key", name="uq_integration_provider_key"),)

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # "stripe", "vipps", ...
    key = Column(String, nullable=False)  # "secret_key", "webhook_secret", ...
    encrypted_value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
