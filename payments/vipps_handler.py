import requests
from typing import Dict, Any, Optional
from datetime import datetime

from models.payment import PaymentProvider
from models.payment_event import PaymentEventType


class VippsHandler:
    """
    Basic skeleton for Vipps integration.
    This will be expanded with:
    - authentication
    - initiate payment
    - webhook validation
    - signature verification
    """

    def __init__(self, client_id: str, client_secret: str, subscription_key: str, merchant_serial_number: str, base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_key = subscription_key
        self.msn = merchant_serial_number
        self.base_url = base_url

    def initiate(self, order_id: int, amount: int, currency: str, return_url: str) -> Dict[str, Any]:
        """
        Placeholder initiate() method.
        Will be implemented fully in next step.
        """
        return {
            "provider": PaymentProvider.VIPPS,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "redirect_url": return_url,
            "message": "Vipps initiate() not implemented yet"
        }

    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str]) -> Dict[str, Any]:
        """
        Placeholder webhook handler.
        Will be implemented fully in next step.
        """
        return {
            "event_type": PaymentEventType.INITIATED,
            "provider": PaymentProvider.VIPPS,
            "order_id": payload.get("orderId", 0),
            "payment_id": payload.get("paymentId", 0),
            "amount": payload.get("amount", 0),
            "currency": payload.get("currency", "NOK"),
            "raw_payload": payload,
            "created_at": datetime.utcnow()
        }
