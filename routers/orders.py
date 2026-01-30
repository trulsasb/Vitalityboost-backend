from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Order not found"}
    return order
