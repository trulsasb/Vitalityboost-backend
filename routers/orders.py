from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models.order import Order

router = APIRouter(prefix="/orders", tags=["Orders"])


# -----------------------------
# Pydantic-skjemaer
# -----------------------------

class OrderCreate(BaseModel):
    total_amount: float


class OrderStatusUpdate(BaseModel):
    status: str


# -----------------------------
# Debug-endepunkt (SQLAlchemy 2.0-kompatibel)
# -----------------------------

@router.get("/debug-enum")
def debug_enum(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT t.typname AS enum_name
        FROM pg_type t
        WHERE t.typtype = 'e';
    """)).fetchall()

    return {"enum_types": [row[0] for row in result]}
@router.get("/debug-enum-values")
def debug_enum_values(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT e.enumlabel
        FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'orderstatus'
        ORDER BY e.enumsortorder;
    """)).fetchall()

    return {"orderstatus_values": [row[0] for row in result]}


# -----------------------------
# Endepunkter
# -----------------------------

@router.post("/")
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        total_amount=payload.total_amount,
        status="created"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/")
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Order not found"}
    return order


@router.put("/{order_id}/status")
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Order not found"}

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
