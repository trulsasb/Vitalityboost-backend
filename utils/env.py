# utils/env.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App‑konfig
    APP_MODE: str = "test"   # test | live

    # Database
    DATABASE_URL: str

    # Betalings‑API‑nøkler
    STRIPE_SECRET_KEY: str
    VIPPS_CLIENT_ID: str
    VIPPS_CLIENT_SECRET: str

    # Regnskap
    TRIPLETEX_TOKEN: str | None = None
    FIKEN_API_KEY: str | None = None

    # E‑post
    SENDGRID_API_KEY: str | None = None

    # Sikkerhet
    JWT_SECRET: str = "supersecret"
    JWT_EXPIRE_HOURS: int = 24

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
