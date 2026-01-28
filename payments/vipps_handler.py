import requests
from typing import Dict, Any, Optional
from datetime import datetime

from models.payment import PaymentProvider
from models.payment_event import PaymentEventType
from .vipps_auth import VippsAuth


class VippsHandler:
    """
    Vipps payment handler.
    Handles:
    - authentication
    - initiate payment
    - webhook processing
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        subscription_key: str,
        merchant_serial_number: str,
        base_url: str,
    ):
        self.auth = VippsAuth(client_id, client_secret, subscription_key, base_url)
        self.msn = merchant_serial_number
        self.base_url = base_url

    def initiate(self, order_id: int, amount: int, currency: str, return_url: str) -> Dict[str, Any]:
        """
        Initiates a Vipps payment session.
        """

        url = f"{self.base_url}/ecomm/v2/payments"

        headers = self.auth.get_headers()
        headers["Merchant-Serial-Number"] = self.msn

        payload = {
            "merchantInfo": {
                "merchantSerialNumber": self.msn,
                "callbackPrefix": return_url,
                "fallBack": return_url,
                "returnUrl": return_url,
            },
            "transaction": {
                "orderId": str(order_id),
                "amount": amount,
                "transactionText": "Vitalityboost purchase",
            },
        }

       response = requests.post(url, json=payload, headers=headers)

try:
    response.raise_for_status()
except Exception:
    print("VIPPS ERROR:", response.text)
    raise

data = response.json()

        return {
            "provider": PaymentProvider.VIPPS,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "redirect_url": data["url"],
            "vipps_reference": data.get("reference"),
        }

    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str]) -> Dict[str, Any]:
        """
        Handles Vipps webhook events.
        """

        event_type = payload.get("event", "").lower()

        if event_type == "payment.captured":
            evt = PaymentEventType.CAPTURED
        elif event_type == "payment.initiated":
            evt = PaymentEventType.INITIATED
        elif event_type == "payment.authorized":
            evt = PaymentEventType.AUTHORIZED
        elif event_type == "payment.refunded":
            evt = PaymentEventType.REFUNDED
        else:
            evt = PaymentEventType.FAILED

        return {
            "event_type": evt,
            "provider": PaymentProvider.VIPPS,
            "order_id": int(payload.get("orderId", 0)),
            "payment_id": int(payload.get("paymentId", 0)),
            "amount": int(payload.get("amount", 0)),
            "currency": payload.get("currency", "NOK"),
            "raw_payload": payload,
            "created_at": datetime.utcnow(),
        }
