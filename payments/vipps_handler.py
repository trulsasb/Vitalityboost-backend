from typing import Optional
from fastapi import HTTPException

from payments.engine import PaymentEngine
from models.payment import PaymentProvider, PaymentStatus


class VippsHandler:
    """
    Hybrid Vipps-handler:
    - Full struktur for ekte Vipps-integrasjon
    - Mock-respons for testing uten API-nøkler
    - 100% kompatibel med PaymentEngine
    """

    def __init__(self, engine: Optional[PaymentEngine] = None):
        self.engine = engine or PaymentEngine()

        # Her kan du senere legge inn ekte Vipps-nøkler:
        # self.client_id = "..."
        # self.client_secret = "..."
        # self.subscription_key = "..."

    # ---------------------------------------------------------
    # INITIATE PAYMENT
    # ---------------------------------------------------------

    def initiate_payment(self, order_id: int) -> dict:
        """
        Oppretter en betaling i PaymentEngine og returnerer
        en mocket Vipps-redirect-URL.

        Når du vil gå live:
        - Opprett ekte Vipps Payment Session
        - Returner redirect-url fra Vipps API
        """

        payment = self.engine.create_payment(
            order_id=order_id,
            provider=PaymentProvider.VIPPS,
        )

        if not payment:
            raise HTTPException(status_code=500, detail="Failed to create payment")

        # Mocket redirect-URL
        mock_redirect_url = f"https://vipps.no/checkout/{payment.id}"

        # Logg event
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
        I ekte Vipps ville dette være en webhook eller polling.
        """

        updated = self.engine.update_status(
            payment_id=payment_id,
            new_status=PaymentStatus.COMPLETED,
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
