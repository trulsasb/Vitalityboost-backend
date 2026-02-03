from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.order import Order, OrderItem
from models.payment import Payment
from models.payment_event import PaymentEvent


router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


# ---------------------------------------------------------
# INTERNAL DB HELPER
# ---------------------------------------------------------

def get_db() -> Session:
    return SessionLocal()


# ---------------------------------------------------------
# LIST ALL ORDERS
# ---------------------------------------------------------

@router.get("/")
def list_orders():
    db = get_db()
    try:
        orders = db.query(Order).all()
        result = []
        for order in orders:
            payments = (
                db.query(Payment)
                .filter(Payment.order_id == order.id)
                .all()
            )
            result.append({
                "id": order.id,
                "created_at": order.created_at,
                "user_id": order.user_id,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                    }
                    for item in order.items
                ],
                "payments": [
                    {
                        "id": p.id,
                        "provider": p.provider,
                        "status": p.status,
                        "amount": p.amount,
                    }
                    for p in payments
                ],
            })
        return result
    finally:
        db.close()


# ---------------------------------------------------------
# GET SINGLE ORDER
# ---------------------------------------------------------

@router.get("/{order_id}")
def get_order(order_id: int):
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        payments = (
            db.query(Payment)
            .filter(Payment.order_id == order.id)
            .all()
        )

        return {
            "id": order.id,
            "created_at": order.created_at,
            "user_id": order.user_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in order.items
            ],
            "payments": [
                {
                    "id": p.id,
                    "provider": p.provider,
                    "status": p.status,
                    "amount": p.amount,
                    "events": [
                        {
                            "id": e.id,
                            "event_type": e.event_type,
                            "data": e.data,
                            "timestamp": e.timestamp,
                        }
                        for e in db.query(PaymentEvent)
                        .filter(PaymentEvent.payment_id == p.id)
                        .all()
                    ],
                }
                for p in payments
            ],
        }
    finally:
        db.close()


# ---------------------------------------------------------
# DELETE ORDER
# ---------------------------------------------------------

@router.delete("/{order_id}")
def delete_order(order_id: int):
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        db.delete(order)
        db.commit()

        return {"deleted": order_id}
    finally:
        db.close()
