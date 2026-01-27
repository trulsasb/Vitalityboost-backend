from fastapi import APIRouter, Request, Depends
from payments.engine import PaymentEngine
from models.payment import PaymentProvider

router = APIRouter(prefix="/webhooks/vipps", tags=["vipps-webhook"])


def get_engine() -> PaymentEngine:
    """
    You will later replace this with a proper dependency injection
    when we wire up PaymentEngine in main.py.
    """
    from main import payment_engine
    return payment_engine


@router.post("/")
async def vipps_webhook(request: Request, engine: PaymentEngine = Depends(get_engine)):
    payload = await request.json()
    signature = request.headers.get("Vipps-Signature")

    engine.process_webhook(
        provider=PaymentProvider.VIPPS,
        payload=payload,
        signature=signature,
    )

    return {"status": "ok"}
