from fastapi import APIRouter, Request, HTTPException
from starlette.responses import JSONResponse

from payments.engine import PaymentEngine
from models.payment import PaymentProvider

router = APIRouter(tags=["Stripe Webhook"])

# Egen instans er greit her – PaymentEngine er stateless ift. DB
payment_engine = PaymentEngine()


@router.post("/")
async def stripe_webhook(request: Request):
    """
    Stripe webhook-endepunkt.
    Forventer et Stripe-event som JSON.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    signature = request.headers.get("Stripe-Signature")

    # Prosesserer webhook generisk via PaymentEngine
    payment_engine.process_webhook(
        provider=PaymentProvider.STRIPE,
        payload=payload,
        signature=signature,
    )

    return JSONResponse({"received": True})
