from fastapi import APIRouter
from payments.vipps_handler import VippsHandler
from payments.stripe_handler import StripeHandler

router = APIRouter()

vipps = VippsHandler()
stripe = StripeHandler()


@router.post("/vipps/initiate")
def initiate_vipps_payment(order_id: int):
    return vipps.initiate_payment(order_id)


@router.post("/stripe/initiate")
def initiate_stripe_payment(order_id: int):
    return stripe.initiate_payment(order_id)
