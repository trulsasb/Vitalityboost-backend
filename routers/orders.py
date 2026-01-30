from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

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
# Debug-endepunkt
# (må stå før {order_id})
# -----------------------------

@router.get("/debug-enum")
def debug_enum(db: Session = Depends(get_db)):
    result = db.execute("""
        SELECT n.nspname AS enum_schema,
               t.typname AS enum_name,
               e.enumlabel AS enum_value
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        ORDER BY enum_schema, enum_name, e.enumsortorder;
    """).fetchall()

    return {
        "enums": [
            {
                "schema": row[0],
                "name": row[1],
                "value": row[2]
            }
            for row in result
        ]
    }


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
