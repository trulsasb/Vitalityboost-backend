from typing import Dict, Any, Optional
from datetime import datetime

from models.payment import PaymentProvider
from models.payment_event import PaymentEventType


class StripeHandler:
    """
    Basic skeleton for Stripe integration.
    This will be expanded with:
    - session creation
    - webhook validation
    - signature verification
    """

    def __init__(self, api_key: str, webhook_secret: str):
        self.api_key = api_key
        self.webhook_secret = webhook_secret

    def initiate(self, order_id: int, amount: int, currency: str, return_url: str) -> Dict[str, Any]:
        """
        Placeholder initiate() method.
        Will be implemented fully in next step.
        """
        return {
            "provider": PaymentProvider.STRIPE,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "redirect_url": return_url,
            "message": "Stripe initiate() not implemented yet"
        }

    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str]) -> Dict[str, Any]:
        """
        Placeholder webhook handler.
        Will be implemented fully in next step.
        """
        return {
            "event_type": PaymentEventType.INITIATED,
            "provider": PaymentProvider.STRIPE,
            "order_id": payload.get("orderId", 0),
            "payment_id": payload.get("paymentId", 0),
            "amount": payload.get("amount", 0),
            "currency": payload.get("currency", "NOK"),
            "raw_payload": payload,
            "created_at": datetime.utcnow()
        }
