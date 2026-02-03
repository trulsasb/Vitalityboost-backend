from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.payment import Payment
from models.payment_event import PaymentEvent

router = APIRouter(prefix="/admin/payments", tags=["Admin Payments"])


@router.get("/")
def list_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()


@router.get("/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/{payment_id}/events")
def list_payment_events(payment_id: int, db: Session = Depends(get_db)):
    events = db.query(PaymentEvent).filter(PaymentEvent.payment_id == payment_id).all()
    if not events:
        raise HTTPException(status_code=404, detail="No events found for this payment")
    return events


@router.post("/{payment_id}/events")
def add_payment_event(payment_id: int, event_type: str, data: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    event = PaymentEvent(payment_id=payment_id, event_type=event_type, data=data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
