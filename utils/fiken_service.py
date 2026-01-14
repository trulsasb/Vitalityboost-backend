import httpx
from fastapi import HTTPException
from utils.env import settings


class FikenService:
    """
    Fiken integrasjon (V2 API).
    Brukes for å sende fakturaer og hente organisasjoner.
    """

    def __init__(self, api_key: str = None, test_mode: bool = settings.APP_MODE == "test"):
        self.api_key = api_key or settings.FIKEN_API_KEY
        self.test_mode = test_mode
        self.base_url = (
            "https://api-test.fiken.no/api/v2"
            if self.test_mode
            else "https://api.fiken.no/api/v2"
        )

    async def _headers(self):
        if not self.api_key:
            raise HTTPException(status_code=400, detail="Fiken API‑key not configured")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def push_invoice(self, invoice_data: dict):
        headers = await self._headers()
        url = f"{self.base_url}/invoices"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=invoice_data)
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()

    async def get_organizations(self):
        headers = await self._headers()
        url = f"{self.base_url}/companies"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return r.json()
