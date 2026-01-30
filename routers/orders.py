from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.product import CartItem, Product
from models.order import Order, OrderItem  # du får denne filen av meg etterpå

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/{session_id}")
def create_order(session_id: str, db: Session = Depends(get_db)):
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.session_id == session_id)
        .all()
    )

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = Order()
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(order_item)

    db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).delete()

    db.commit()
    return {"order_id": order.id, "status": "created"}
