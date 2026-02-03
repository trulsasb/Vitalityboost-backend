from fastapi import APIRouter, HTTPException

from payments.stripe_handler import StripeHandler
from payments.vipps_handler import VippsHandler

stripe = StripeHandler()
vipps = VippsHandler()

router = APIRouter(prefix="/payments", tags=["Payments"])


# ---------------------------------------------------------
# STRIPE INITIATE PAYMENT
# ---------------------------------------------------------

@router.post("/stripe/initiate/{order_id}")
def initiate_stripe_payment(order_id: int):
    """
    Start a Stripe payment (mock).
    """
    try:
        return stripe.initiate_payment(order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# VIPPS INITIATE PAYMENT
# ---------------------------------------------------------

@router.post("/vipps/initiate/{order_id}")
def initiate_vipps_payment(order_id: int):
    """
    Start a Vipps payment (mock).
    """
    try:
        return vipps.initiate_payment(order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# GENERIC MOCK CONFIRMATION
# ---------------------------------------------------------

@router.post("/confirm/{payment_id}")
def confirm_payment(payment_id: int):
    """
    Mock confirmation for both Stripe and Vipps.
    """
    # Stripe first
    try:
        return stripe.confirm_payment(payment_id)
    except Exception:
        pass

    # Then Vipps
    try:
        return vipps.confirm_payment(payment_id)
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Payment not found")
