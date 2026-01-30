from sqlalchemy.orm import Session
from database import SessionLocal
from models.order import Order
from models.payment import Payment
from models.payment_event import PaymentEvent


class VippsHandler:
    def initiate_payment(self, order_id: int):
        db: Session = SessionLocal()

        # Fetch order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            db.close()
            return {"error": f"Order {order_id} not found"}

        # Create payment
        payment = Payment(
            order_id=order.id,
            provider="vipps",
            status="initiated",
            amount=order.total_amount,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Log event
        event = PaymentEvent(
            payment_id=payment.id,
            event_type="initiated",
            data=f"Vipps payment initiated for order {order.id}",
        )
        db.add(event)
        db.commit()

        db.close()

        return {
            "payment_id": payment.id,
            "redirect_url": f"https://vipps.no/checkout/{payment.id}"
        }
