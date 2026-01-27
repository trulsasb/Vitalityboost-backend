from fastapi import APIRouter, Request, Depends, HTTPException
from payments.engine import PaymentEngine
from models.payment import PaymentProvider
import stripe

router = APIRouter(prefix="/webhooks/stripe", tags=["stripe-webhook"])


def get_engine() -> PaymentEngine:
    """
    Temporary dependency until we wire up PaymentEngine in main.py.
    """
    from main import payment_engine
    return payment_engine


@router.post("/")
async def stripe_webhook(request: Request, engine: PaymentEngine = Depends(get_engine)):
    # Stripe requires raw body for signature verification
    raw_body = await request.body()
    signature = request.headers.get("Stripe-Signature")

    # Get webhook secret from handler
    webhook_secret = engine.handlers[PaymentProvider.STRIPE].webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload=raw_body,
            sig_header=signature,
            secret=webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    # Pass the verified event to the engine
    engine.process_webhook(
        provider=PaymentProvider.STRIPE,
        payload=event,
        signature=signature,
    )

    return {"status": "ok"}
