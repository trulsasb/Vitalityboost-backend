# utils/validators.py
import re
from fastapi import HTTPException


def validate_email(email: str):
    """Enkel epost‑validering."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        raise HTTPException(status_code=400, detail="Invalid email address")


def validate_amount(amount: float):
    """Sikrer at beløp er gyldig og positivt."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")


def validate_api_key(key: str, provider: str):
    """Generell validering av API-nøkler."""
    if not key or len(key) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Missing or invalid API key for {provider}",
        )
