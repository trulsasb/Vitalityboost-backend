from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderItem, OrderStatus
from schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    order = Order()
    db.add(order)
    db.commit()
    db.refresh(order)

    total_amount = 0

    for item in order_data.items:
        price = 499  # midlertidig pris, du kan hente fra DB senere
        total_amount += price * item.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=price,
        )
        db.add(order_item)

    order.total_amount = total_amount
    db.commit()
    db.refresh(order)

    return order


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_update.status
    db.commit()
    db.refresh(order)

    return order
