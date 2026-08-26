import httpx
from fastapi import HTTPException
from utils.env import settings


class EmailService:
    """
    Håndterer utsending av ordrebekreftelser og admin‑varsler.
    Bruker SendGrid i produksjon og MailHog i testmodus.
    """

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.test_mode = settings.APP_MODE == "test"
        self.mailhog_url = "http://mailhog:8025"

    async def send_order_confirmation(self, to_email: str, subject: str, body: str):
        return await self._send(to_email, subject, body)

    async def send_notification(self, to_email: str, subject: str, body: str):
        """Generic outbound email -- e.g. a contact-form submission -- distinct
        from send_order_confirmation only by name, so call sites read clearly."""
        return await self._send(to_email, subject, body)

    async def _send(self, to_email: str, subject: str, body: str):
        if self.test_mode:
            print(f"[TEST-MAIL] To: {to_email} - {subject}")
            return {"status": "simulated"}
        if not self.api_key:
            raise HTTPException(status_code=400, detail="SendGrid key missing")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": "no-reply@vitalityboost.no"},
            "subject": subject,
            "content": [{"type": "text/html", "value": body}]
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send", headers=headers, json=data
            )
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return {"status": "sent"}
