from fastapi import APIRouter, Request, Depends
from payments.engine import PaymentEngine
from models.payment import PaymentProvider

router = APIRouter(prefix="/webhooks/stripe", tags=["stripe-webhook"])


def get_engine() -> PaymentEngine:
    """
    Temporary dependency until we wire up PaymentEngine in main.py.
    """
    from main import payment_engine
    return payment_engine


@router.post("/")
async def stripe_webhook(request: Request, engine: PaymentEngine = Depends(get_engine)):
    payload = await request.json()
    signature = request.headers.get("Stripe-Signature")

    engine.process_webhook(
        provider=PaymentProvider.STRIPE,
        payload=payload,
        signature=signature,
    )

    return {"status": "ok"}
