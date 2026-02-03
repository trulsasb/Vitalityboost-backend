from typing import Optional
from fastapi import HTTPException

from payments.engine import PaymentEngine


class VippsHandler:
    """
    Hybrid Vipps-handler:
    - Full struktur for ekte Vipps-integrasjon
    - Mock-respons for testing uten API-nøkler
    - 100% kompatibel med PaymentEngine
    """

    def __init__(self, engine: Optional[PaymentEngine] = None):
        self.engine = engine or PaymentEngine

    # ---------------------------------------------------------
    # INITIATE PAYMENT
    # ---------------------------------------------------------

    def initiate_payment(self, order_id: int, amount: float = 0.0) -> dict:
        """
        Oppretter en betaling i PaymentEngine og returnerer
        en mocket Vipps-redirect-URL.
        """

        payment = self.engine.create_payment(
            order_id=order_id,
            provider="vipps",
            amount=amount,
        )

        if not payment:
            raise HTTPException(status_code=500, detail="Failed to create payment")

        mock_redirect_url = f"https://vipps.no/checkout/{payment.id}"

        self.engine.add_event(
            payment_id=payment.id,
            event_type="vipps_mock_initiated",
            data=f"redirect_url={mock_redirect_url}",
        )

        return {
            "payment_id": payment.id,
            "provider": "vipps",
            "amount": payment.amount,
            "redirect_url": mock_redirect_url,
            "status": payment.status,
        }

    # ---------------------------------------------------------
    # CONFIRM PAYMENT (MOCK)
    # ---------------------------------------------------------

    def confirm_payment(self, payment_id: int) -> dict:
        """
        Mocket bekreftelse av betaling.
        """

        updated = self.engine.update_status(
            payment_id=payment_id,
            new_status="completed",
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Payment not found")

        self.engine.add_event(
            payment_id=payment_id,
            event_type="vipps_mock_confirmed",
            data="Payment marked as completed",
        )

        return {
            "payment_id": payment_id,
            "status": updated.status,
        }
