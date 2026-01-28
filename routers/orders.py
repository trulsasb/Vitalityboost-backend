from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models.order import Order, OrderItem, OrderStatus
from models.product import Product


router = APIRouter(prefix="/orders", tags=["Orders"])


# -----------------------------
#   SCHEMAS
# -----------------------------

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


# -----------------------------
#   CREATE ORDER
# -----------------------------

@router.post("/", response_model=dict)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    total_amount = 0
    order_items = []

    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        total_amount += int(product.price) * item.quantity

        order_items.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price
            )
        )

    order = Order(
        total_amount=total_amount,
        status=OrderStatus.PENDING_PAYMENT,
        items=order_items
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
    }


# -----------------------------
#   GET ORDER
# -----------------------------

@router.get("/{order_id}", response_model=dict)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_purchase": item.price_at_purchase
            }
            for item in order.items
        ]
    }
