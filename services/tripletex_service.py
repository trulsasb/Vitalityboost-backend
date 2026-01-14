import httpx
from fastapi import HTTPException
from utils.env import settings


class TripletexService:
    """
    Tripletex integrasjon for fakturering / regnskap.
    """

    def __init__(self, api_key: str = None, test_mode: bool = settings.APP_MODE == "test"):
        self.api_key = api_key or settings.TRIPLETEX_TOKEN
        self.test_mode = test_mode
        self.base_url = (
            "https://api.test.tripletex.io/v2"
            if self.test_mode
            else "https://api.tripletex.io/v2"
        )

    async def _headers(self):
        if not self.api_key:
            raise HTTPException(status_code=400, detail="Tripletex API‑key not configured")
        return {"Authorization": f"Basic {self.api_key}"}

    async def post_invoice(self, invoice_data: dict):
        headers = await self._headers()
        url = f"{self.base_url}/invoice"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=invoice_data)
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()

    async def test_connection(self):
        headers = await self._headers()
        url = f"{self.base_url}/token/session"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            if r.status_code >= 400:
                return {"success": False, "error": r.text}
            return {"success": True}
