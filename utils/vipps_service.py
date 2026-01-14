import httpx
from fastapi import HTTPException
from utils.env import settings


class VippsService:
    """
    Vipps integrasjon (v3 ePayment API).
    Bruker test‑ eller produksjons‑endpoint automatisk.
    """

    def __init__(self):
        self.base = (
            "https://apitest.vipps.no" if settings.APP_MODE == "test"
            else "https://api.vipps.no"
        )
        self.client_id = settings.VIPPS_CLIENT_ID
        self.secret = settings.VIPPS_CLIENT_SECRET

    async def initiate_payment(self, amount: float, order_id: str):
        headers = {
            "client_id": self.client_id,
            "client_secret": self.secret,
            "Content-Type": "application/json"
        }
        data = {
            "amount": amount,
            "orderId": order_id,
            "currency": "NOK",
            "customer": {"email": "test@example.com"},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base}/ecomm/v2/payments",
                headers=headers, json=data,
            )
            if response.status_code >= 400:
                raise HTTPException(status_code=400, detail=response.text)
            return response.json()

    async def capture_payment(self, payment_id: str):
        headers = {
            "client_id": self.client_id,
            "client_secret": self.secret,
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base}/ecomm/v2/payments/{payment_id}/capture",
                headers=headers,
            )
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return r.json()
