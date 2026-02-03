from fastapi import APIRouter, Request, HTTPException
from starlette.responses import JSONResponse

from payments.engine import PaymentEngine
from models.payment import PaymentProvider

router = APIRouter(tags=["Vipps Webhook"])

payment_engine = PaymentEngine()


@router.post("/")
async def vipps_webhook(request: Request):
    """
    Vipps webhook-endepunkt.
    Forventer et JSON-payload fra Vipps.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Vipps-signatur kan evt. hentes fra header senere
    signature = request.headers.get("X-Vipps-Signature")

    payment_engine.process_webhook(
        provider=PaymentProvider.VIPPS,
        payload=payload,
        signature=signature,
    )

    return JSONResponse({"received": True})
