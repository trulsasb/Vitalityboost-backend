from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from payments.stripe_handler import StripeHandler
from payments.vipps_handler import VippsHandler

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/stripe/initiate")
def initiate_stripe_payment(order_id: int, amount: float, db: Session = Depends(get_db)):
    handler = StripeHandler()
    return handler.initiate_payment(order_id=order_id, amount=amount)


@router.post("/vipps/initiate")
def initiate_vipps_payment(order_id: int, db: Session = Depends(get_db)):
    handler = VippsHandler()
    return handler.initiate_payment(order_id=order_id)

