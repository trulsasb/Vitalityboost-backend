from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.order import OrderCreate, OrderResponse
from models.order import Order, OrderItem
from models.product import Product

router = APIRouter()

# -----------------------------
#   CREATE ORDER
# -----------------------------
@router.post("/", response_model=OrderResponse)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    order = Order(status="pending_payment")
    db.add(order)
    db.commit()
    db.refresh(order)

    total_amount = 0

    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price
