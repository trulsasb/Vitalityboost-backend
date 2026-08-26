# utils/env.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App‑konfig
    APP_MODE: str = "test"   # test | live

    # Database
    DATABASE_URL: str = "sqlite:///./vitalityboost.db"

    # Betalings‑API‑nøkler
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    VIPPS_CLIENT_ID: str | None = None
    VIPPS_CLIENT_SECRET: str | None = None
    VIPPS_SUBSCRIPTION_KEY: str | None = None
    VIPPS_MSN: str | None = None  # Merchant Serial Number
    VIPPS_BASE_URL: str = "https://apitest.vipps.no"
    VIPPS_WEBHOOK_SECRET: str | None = None  # returned when registering the webhook via POST /webhooks
    FRONTEND_URL: str = "https://vitalityboost.no"

    # Regnskap
    TRIPLETEX_TOKEN: str | None = None
    FIKEN_API_KEY: str | None = None

    # E‑post
    SENDGRID_API_KEY: str | None = None
    # Fallback contact-form recipient, used until an admin sets one via the
    # dashboard (stored in site_settings, key "contact_notify_email").
    CONTACT_EMAIL: str = "kontakt@vitalityboost.no"

    # Sikkerhet
    JWT_SECRET: str = "supersecret"
    JWT_EXPIRE_HOURS: int = 24

    # Fernet key used to encrypt payment-provider credentials stored in the
    # database (Stripe/Vipps keys entered via the admin dashboard). Generate
    # with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    SETTINGS_ENCRYPTION_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# Refuse to boot in live mode with the placeholder JWT secret still in place —
# this would let anyone forge a valid admin token.
if settings.APP_MODE == "live" and settings.JWT_SECRET == "supersecret":
    raise RuntimeError(
        "JWT_SECRET is still the default placeholder. Set a real random "
        "JWT_SECRET env var before running in live mode."
    )
