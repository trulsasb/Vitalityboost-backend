from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.orm import Session

from models.integration_setting import IntegrationSetting
from utils.env import settings


def _cipher() -> Fernet:
    if not settings.SETTINGS_ENCRYPTION_KEY:
        raise RuntimeError(
            "SETTINGS_ENCRYPTION_KEY is not configured — cannot store or read "
            "encrypted integration credentials until it's set."
        )
    return Fernet(settings.SETTINGS_ENCRYPTION_KEY.encode())


def encrypt_value(value: str) -> str:
    return _cipher().encrypt(value.encode()).decode()


def decrypt_value(token: str) -> str:
    return _cipher().decrypt(token.encode()).decode()


def get_setting(db: Session, provider: str, key: str) -> str | None:
    """Decrypted value stored via the admin dashboard for this provider/key,
    or None if nothing's been saved there yet."""
    row = (
        db.query(IntegrationSetting)
        .filter(IntegrationSetting.provider == provider, IntegrationSetting.key == key)
        .first()
    )
    if not row:
        return None
    try:
        return decrypt_value(row.encrypted_value)
    except InvalidToken:
        # SETTINGS_ENCRYPTION_KEY changed since this was saved — treat as unset
        # rather than crashing the caller.
        return None


def resolve_setting(db: Session, provider: str, key: str, env_fallback: str | None) -> str | None:
    """Dashboard-saved value takes priority; falls back to the Render
    environment variable so existing env-var-based deployments keep working
    until someone actually uses the dashboard for that provider."""
    return get_setting(db, provider, key) or env_fallback


def set_settings(db: Session, provider: str, values: dict[str, str]) -> None:
    for key, value in values.items():
        if not value:
            continue
        row = (
            db.query(IntegrationSetting)
            .filter(IntegrationSetting.provider == provider, IntegrationSetting.key == key)
            .first()
        )
        encrypted = encrypt_value(value)
        if row:
            row.encrypted_value = encrypted
        else:
            db.add(IntegrationSetting(provider=provider, key=key, encrypted_value=encrypted))
    db.commit()
