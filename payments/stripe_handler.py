import os
import stripe
from database import SessionLocal
from models.payment import Payment, PaymentEvent, PaymentProvider, PaymentStatus
from datetime import datetime


class StripeHandler:
    def __init__(self):
        self.db = SessionLocal()
        stripe.api_key = os.getenv("STRIPE_API_KEY")

    def initiate_payment(self, order):
        payment = Payment(
            order_id=order.id,
            provider=PaymentProvider.STRIPE,
            status=PaymentStatus.INITIATED,
            amount=order.total_amount,
            currency="NOK",
            created_at=datetime.utcnow(),
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        self._log_event(payment.id, "initiated")

        # Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "nok",
                        "product_data": {"name": f"Order {order.id}"},
                        "unit_amount": order.total_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        payment.provider_reference = session.id
        self.db.commit()

        return {
            "payment_id": payment.id,
            "redirect_url": session.url,
        }

    def _log_event(self, payment_id: int, event_type: str, raw_data: str = None):
        event = PaymentEvent(
            payment_id=payment_id,
            event_type=event_type,
            raw_data=raw_data,
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
