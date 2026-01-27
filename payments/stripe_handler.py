import stripe
from typing import Dict, Any, Optional
from datetime import datetime

from models.payment import PaymentProvider
from models.payment_event import PaymentEventType


class StripeHandler:
    """
    Stripe integration using Checkout Sessions.
    """

    def __init__(self, api_key: str, webhook_secret: str):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        stripe.api_key = api_key

    def initiate(self, order_id: int, amount: int, currency: str, return_url: str) -> Dict[str, Any]:
        """
        Creates a Stripe Checkout Session.
        """

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {"name": f"Order #{order_id}"},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{return_url}?order_id={order_id}&status=success",
            cancel_url=f"{return_url}?order_id={order_id}&status=cancel",
            metadata={"order_id": order_id},
        )

        return {
            "provider": PaymentProvider.STRIPE,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "redirect_url": session.url,
            "stripe_session_id": session.id,
        }

    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str]) -> Dict[str, Any]:
        """
        Handles Stripe webhook events.
        """

        event_type = payload.get("type", "")

        if event_type == "checkout.session.completed":
            evt = PaymentEventType.CAPTURED
        elif event_type == "payment_intent.succeeded":
            evt = PaymentEventType.CAPTURED
        elif event_type == "payment_intent.payment_failed":
            evt = PaymentEventType.FAILED
        else:
            evt = PaymentEventType.INITIATED

        data = payload.get("data", {}).get("object", {})

        return {
            "event_type": evt,
            "provider": PaymentProvider.STRIPE,
            "order_id": int(data.get("metadata", {}).get("order_id", 0)),
            "payment_id": data.get("id"),
            "amount": int(data.get("amount_total", 0)),
            "currency": data.get("currency", "nok").upper(),
            "raw_payload": payload,
            "created_at": datetime.utcnow(),
        }
