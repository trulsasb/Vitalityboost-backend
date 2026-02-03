from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.payment import Payment
from models.payment_event import PaymentEvent


router = APIRouter(prefix="/admin/payments", tags=["Admin Payments"])


def get_db() -> Session:
    return SessionLocal()


@router.get("/")
def list_payments():
    db = get_db()
    try:
        payments = db.query(Payment).all()
        return [
            {
                "id": p.id,
                "order_id": p.order_id,
                "provider": p.provider,
                "status": p.status,
                "amount": p.amount,
            }
            for p in payments
        ]
    finally:
        db.close()


@router.get("/{payment_id}")
def get_payment(payment_id: int):
    db = get_db()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        events = (
            db.query(PaymentEvent)
            .filter(PaymentEvent.payment_id == payment.id)
            .all()
        )

        return {
            "id": payment.id,
            "order_id": payment.order_id,
            "provider": payment.provider,
            "status": payment.status,
            "amount": payment.amount,
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "data": e.data,
                    "timestamp": e.timestamp,
                }
                for e in events
            ],
        }
    finally:
        db.close()


@router.delete("/{payment_id}")
def delete_payment(payment_id: int):
    db = get_db()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        db.delete(payment)
        db.commit()

        return {"deleted": payment_id}
    finally:
        db.close()
