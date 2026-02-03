from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from database import SessionLocal
from models.order import Order, OrderItem
from models.product import Product
from models.payment import Payment, PaymentEvent, PaymentProvider, PaymentStatus


class ProviderConfig:
    """
    Holder provider-spesifikk konfigurasjon (webhook-secrets osv.)
    """
    def __init__(self, webhook_secret: Optional[str] = None):
        self.webhook_secret = webhook_secret


class PaymentEngine:
    """
    Sentral motor for:
    - Opprettelse av betalinger
    - Logging av events
    - Oppdatering av status
    - Webhook-prosessering
    """

    def __init__(self):
        self.handlers: Dict[PaymentProvider, ProviderConfig] = {
            PaymentProvider.STRIPE: ProviderConfig(),
            PaymentProvider.VIPPS: ProviderConfig(),
        }

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------

    def _get_db(self) -> Session:
        return SessionLocal()

    def _calculate_order_total(self, db: Session, order: Order) -> float:
        """
        Summerer totalbeløpet basert på ordrelinjer og produktpriser.
        """
        items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        total = 0.0
        for item in items:
            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .first()
            )
            if product:
                total += item.quantity * product.price

        return total

    # ---------------------------------------------------------
    # PAYMENT CREATION
    # ---------------------------------------------------------

    def create_payment(
        self,
        order_id: int,
        provider: PaymentProvider,
    ) -> Payment:
        """
        Oppretter en betaling for en ordre.
        """
        db = self._get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError(f"Order {order_id} not found")

            amount = self._calculate_order_total(db, order)

            payment = Payment(
                order_id=order.id,
                provider=provider.value if hasattr(provider, "value") else provider,
                status=PaymentStatus.INITIATED.value
                if hasattr(PaymentStatus, "INITIATED")
                else "initiated",
                amount=amount,
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)
            return payment

        finally:
            db.close()

    # ---------------------------------------------------------
    # EVENT LOGGING
    # ---------------------------------------------------------

    def add_event(
        self,
        payment_id: int,
        event_type: str,
        data: Optional[str] = None,
    ) -> PaymentEvent:
        """
        Logger et event knyttet til en betaling.
        """
        db = self._get_db()
        try:
            event = PaymentEvent(
                payment_id=payment_id,
                event_type=event_type,
                data=data,
                timestamp=datetime.utcnow(),
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event

        finally:
            db.close()

    # ---------------------------------------------------------
    # STATUS UPDATE
    # ---------------------------------------------------------

    def update_status(
        self,
        payment_id: int,
        new_status: PaymentStatus,
    ) -> Optional[Payment]:
        """
        Oppdaterer status på en betaling.
        """
        db = self._get_db()
        try:
            payment = (
                db.query(Payment)
                .filter(Payment.id == payment_id)
