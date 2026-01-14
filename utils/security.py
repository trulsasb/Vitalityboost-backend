# utils/security.py
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.env import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


def create_jwt_token(email: str) -> str:
    """Lager et signert JWT-token for bruker‑autentisering."""
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def decode_jwt_token(token: str) -> dict:
    """Dekoder et gyldig JWT-token og returnerer payload."""
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """FastAPI Dependency for å hente innlogget bruker."""
    payload = decode_jwt_token(token)
    return payload.get("sub")
