from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderItem, OrderStatus
from models.product import Product
from schemas.order import OrderCreate, OrderResponse

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Opprett selve ordren
    order = Order(
        total_amount=0,
        status=OrderStatus.PENDING_PAYMENT
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    total_amount = 0

    # Legg til order items
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price
        )
        db.add(order_item)

        total_amount += product.price * item.quantity

    # Oppdater total_amount
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
