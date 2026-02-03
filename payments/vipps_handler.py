from sqlalchemy.orm import Session
from database import SessionLocal
from models.order import Order, OrderItem
from models.product import Product
from models.payment import Payment
from models.payment_event import PaymentEvent


class VippsHandler:
    def initiate_payment(self, order_id: int):
        db: Session = SessionLocal()

        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            db.close()
            return {"error": f"Order {order_id} not found"}

        # Beregn total_amount basert på OrderItem og Product.price
        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        total_amount = 0.0
        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                total_amount += item.quantity * product.price

        payment = Payment(
            order_id=order.id,
            provider="vipps",
            status="initiated",
            amount=total_amount,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

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
            "redirect_url": f"https://vipps.no/checkout/{payment.id}",
        }
