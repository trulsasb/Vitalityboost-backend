import hashlib
import hmac
import random
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from services.email_service import EmailService
from utils.env import settings
from utils.site_settings import get_site_setting

router = APIRouter(prefix="/contact", tags=["Contact"])

CONTACT_EMAIL_KEY = "contact_notify_email"
_CHALLENGE_TTL_SECONDS = 600  # 10 minutes to fill out the form before it expires


def _sign_challenge(a: int, b: int, issued_at: int) -> str:
    payload = f"{a}:{b}:{issued_at}".encode()
    return hmac.new(settings.JWT_SECRET.encode(), payload, hashlib.sha256).hexdigest()


@router.get("/challenge")
def get_challenge():
    """Stateless 'prove you're human' check: a small math question whose
    answer is verified server-side via a signed token, so no session/DB
    storage is needed just to ask '3 + 5 = ?'."""
    a, b = random.randint(1, 9), random.randint(1, 9)
    issued_at = int(time.time())
    return {
        "a": a,
        "b": b,
        "issued_at": issued_at,
        "token": _sign_challenge(a, b, issued_at),
    }


class ContactSubmission(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    message: str = Field(min_length=1, max_length=5000)
    challenge_a: int
    challenge_b: int
    challenge_issued_at: int
    challenge_token: str
    challenge_answer: int
    website: str = ""  # honeypot -- real visitors never see or fill this in


@router.post("/")
async def submit_contact_form(payload: ContactSubmission, db: Session = Depends(get_db)):
    if payload.website:
        # A bot filled the hidden honeypot field. Report success anyway so
        # it doesn't learn this check exists.
        return {"status": "sent"}

    if time.time() - payload.challenge_issued_at > _CHALLENGE_TTL_SECONDS:
        raise HTTPException(status_code=400, detail="Bekreftelsen har utløpt, prøv igjen")

    expected_token = _sign_challenge(payload.challenge_a, payload.challenge_b, payload.challenge_issued_at)
    if not hmac.compare_digest(expected_token, payload.challenge_token):
        raise HTTPException(status_code=400, detail="Ugyldig bekreftelse")

    if payload.challenge_answer != payload.challenge_a + payload.challenge_b:
        raise HTTPException(status_code=400, detail="Feil svar på kontrollspørsmålet")

    notify_email = get_site_setting(db, CONTACT_EMAIL_KEY) or settings.CONTACT_EMAIL

    subject = f"Ny henvendelse fra {payload.name} via kontaktskjema"
    body = (
        f"<p><strong>Navn:</strong> {payload.name}</p>"
        f"<p><strong>E-post:</strong> {payload.email}</p>"
        f"<p><strong>Melding:</strong></p><p>{payload.message}</p>"
    )

    try:
        await EmailService().send_notification(notify_email, subject, body)
    except Exception as e:
        print(f"[contact-form] failed to send notification email: {e}")
        raise HTTPException(
            status_code=502,
            detail="Kunne ikke sende meldingen akkurat nå. Prøv igjen senere, eller ta kontakt direkte.",
        )

    return {"status": "sent"}
