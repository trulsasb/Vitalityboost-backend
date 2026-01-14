import stripe
from fastapi import HTTPException
from utils.env import settings

class StripeService:
    """
    Stripe‑integrasjon for kort‑betalinger.
    Støtter test‑ og live‑modus avhengig av APP_MODE‑variabel.
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, amount, currency="nok"):
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency,
                payment_method_types=["card"],
            )
            return intent.client_secret
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def retrieve_payment_intent(self, intent_id: str):
        try:
            return stripe.PaymentIntent.retrieve(intent_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
