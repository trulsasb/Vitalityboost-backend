from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from database import SessionLocal
from models.order import Order, OrderItem
from models.product import Product
from models.payment import Payment, PaymentEvent, PaymentProvider, PaymentStatus


class ProviderConfig:
    def __init__(self, webhook_secret: Optional[str] = None):
        self.webhook_secret = webhook_secret


class PaymentEngine:
    def __init__(self):
        # Registry for provider-spesifikk konfigurasjon (webhook-secrets osv.)
        # Selve handlerne for initiering (StripeHandler/VippsHandler) lever separat.
        self.handlers: Dict[PaymentProvider, ProviderConfig] = {
            PaymentProvider.STRIPE: ProviderConfig(),
            PaymentProvider.VIPPS: ProviderConfig(),
        }

    def _get_db(self) -> Session:
        return SessionLocal()

    def _calculate_order_total(self, db: Session, order: Order) -> float:
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

    def create_payment(
        self,
        order_id: int,
        provider: PaymentProvider,
    ) -> Payment:
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

    def add_event(
        self,
        payment_id: int,
        event_type: str,
        data: Optional[str] = None,
    ) -> PaymentEvent:
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

    def update_status(
        self,
        payment_id: int,
        new_status: PaymentStatus,
    ) -> Optional[Payment]:
        db = self._get_db()
        try:
            payment = (
                db.query(Payment)
                .filter(Payment.id == payment_id)
                .first()
            )
            if not payment:
                return None

            payment.status = (
                new_status.value
                if hasattr(new_status, "value")
                else new_status
            )
            db.commit()
            db.refresh(payment)
            return payment
        finally:
            db.close()

    def process_webhook(
        self,
        provider: PaymentProvider,
        payload: Any,
        signature: Optional[str] = None,
    ) -> None:
        """
        Generisk webhook-prosessering:
        - Parser provider-spesifikk payload
        - Oppdaterer Payment-status
        - Logger PaymentEvent
        """
        db = self._get_db()
        try:
            payment_id, new_status = self._extract_payment_update(provider, payload)

            if payment_id is None or new_status is None:
                return

            payment = (
                db.query(Payment)
                .filter(Payment.id == payment_id)
                .first()
            )
            if not payment:
                return

            payment.status = (
                new_status.value
                if hasattr(new_status, "value")
                else new_status
            )
            db.commit()
            db.refresh(payment)

            event = PaymentEvent(
                payment_id=payment.id,
                event_type="webhook",
                data=str(payload),
                timestamp=datetime.utcnow(),
            )
            db.add(event)
            db.commit()
        finally:
            db.close()

    def _extract_payment_update(
        self,
        provider: PaymentProvider,
        payload: Any,
    ) -> (Optional[int], Optional[PaymentStatus]):
        """
        Provider-spesifikk parsing av webhook-payload.
        Denne er bevisst enkel og kan utvides når du kobler på ekte Stripe/Vipps.
        """
        # Stripe: forventer at payload er et event-objekt
        if provider == PaymentProvider.STRIPE:
            # Eksempel: hent payment_id fra metadata
            try:
                obj = payload["data"]["object"]
                payment_id = int(obj["metadata"]["payment_id"])
                status_raw = obj.get("status", "succeeded")
            except Exception:
                return None, None

            status = self._map_stripe_status(status_raw)
            return payment_id, status

        # Vipps: forventer JSON med paymentId og status
        if provider == PaymentProvider.VIPPS:
            try:
                payment_id = int(payload.get("paymentId"))
                status_raw = payload.get("status", "COMPLETED")
            except Exception:
                return None, None

            status = self._map_vipps_status(status_raw)
            return payment_id, status

        return None, None

    def _map_stripe_status(self, status_raw: str) -> PaymentStatus:
        status_raw = status_raw.lower()
        if status_raw in ("succeeded", "paid"):
            return (
                PaymentStatus.COMPLETED
                if hasattr(PaymentStatus, "COMPLETED")
                else "completed"
            )
        if status_raw in ("failed", "canceled"):
            return (
                PaymentStatus.FAILED
                if hasattr(PaymentStatus, "FAILED")
                else "failed"
            )
        return (
            PaymentStatus.PENDING
            if hasattr(PaymentStatus, "PENDING")
            else "pending"
        )

    def _map_vipps_status(self, status_raw: str) -> PaymentStatus:
        status_raw = status_raw.upper()
        if status_raw in ("COMPLETED", "CAPTURED"):
            return (
                PaymentStatus.COMPLETED
                if hasattr(PaymentStatus, "COMPLETED")
                else "completed"
            )
        if status_raw in ("FAILED", "CANCELLED"):
            return (
                PaymentStatus.FAILED
                if hasattr(PaymentStatus, "FAILED")
                else "failed"
            )
        return (
            PaymentStatus.PENDING
            if hasattr(PaymentStatus, "PENDING")
            else "pending"
        )
