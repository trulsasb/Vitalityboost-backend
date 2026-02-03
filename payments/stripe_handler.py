from typing import Optional
from fastapi import HTTPException

from payments.engine import PaymentEngine
from models.payment import PaymentProvider, PaymentStatus


class StripeHandler:
    """
    Hybrid Stripe-handler:
    - Full struktur for ekte Stripe-integrasjon
    - Mock-respons for testing uten API-nøkler
    - 100% kompatibel med PaymentEngine
    """

    def __init__(self, engine: Optional[PaymentEngine] = None):
        self.engine = engine or PaymentEngine()

        # Her kan du senere legge inn ekte Stripe-nøkler:
        # self.secret_key = "sk_live_..."
        # self.public_key = "pk_live_..."

    # ---------------------------------------------------------
    # INITIATE PAYMENT
    # ---------------------------------------------------------

    def initiate_payment(self, order_id: int) -> dict:
        """
        Oppretter en betaling i PaymentEngine og returnerer
        en mocket Stripe PaymentIntent-lignende respons.

        Når du vil gå live:
        - Opprett ekte PaymentIntent via Stripe API
        - Returner client_secret
        """

        payment = self.engine.create_payment(
            order_id=order_id,
            provider=PaymentProvider.STRIPE,
        )

        if not payment:
            raise HTTPException(status_code=500, detail="Failed to create payment")

        # Mocket PaymentIntent
        mock_client_secret = f"pi_mock_{payment.id}_secret_123"

        # Logg event
        self.engine.add_event(
            payment_id=payment.id,
            event_type="stripe_mock_initiated",
            data=f"client_secret={mock_client_secret}",
        )

        return {
            "payment_id": payment.id,
            "provider": "stripe",
            "amount": payment.amount,
            "client_secret": mock_client_secret,
            "status": payment.status,
        }

    # ---------------------------------------------------------
    # CONFIRM PAYMENT (MOCK)
    # ---------------------------------------------------------

    def confirm_payment(self, payment_id: int) -> dict:
        """
        Mocket bekreftelse av betaling.
        I ekte Stripe ville dette være en webhook eller PaymentIntent polling.
        """

        updated = self.engine.update_status(
            payment_id=payment_id,
            new_status=PaymentStatus.COMPLETED,
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Payment not found")

        self.engine.add_event(
            payment_id=payment_id,
            event_type="stripe_mock_confirmed",
            data="Payment marked as completed",
        )

        return {
            "payment_id": payment_id,
            "status": updated.status,
        }
