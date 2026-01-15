from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.stripe_service import StripeService

from services.vipps_service import VippsService

from models import models, database


router = APIRouter()

class PaymentIn(BaseModel):
    order_id: str
    amount: float
    method: str   # "stripe" or "vipps"

class PaymentOut(BaseModel):
    status: str
    transaction_id: str | None = None
    detail: dict | None = None


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PaymentOut)
async def initiate_payment(payload: PaymentIn, db: Session = Depends(get_db)):
    if payload.method == "stripe":
        stripe_service = StripeService()
        intent_secret = stripe_service.create_payment_intent(payload.amount)
        return {"status": "initiated", "transaction_id": intent_secret}
    elif payload.method == "vipps":
        vipps_service = VippsService()
        data = await vipps_service.initiate_payment(payload.amount, payload.order_id)
        return {"status": "initiated", "detail": data}
    else:
        raise HTTPException(status_code=400, detail="Unsupported payment method")
