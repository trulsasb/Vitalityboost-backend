from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.product import CartItem
from models.order import Order, OrderItem
from models.payment import Payment

router = APIRouter(prefix="/orders", tags=["Orders"])


# ---------------------------------------------------------
# CREATE ORDER (PUBLIC)
# ---------------------------------------------------------

@router.post("/{session_id}")
def create_order(session_id: str, db: Session = Depends(get_db)):
    """
    Create an order from the cart items belonging to a session.
    """
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


# ---------------------------------------------------------
# ADMIN: LIST ALL ORDERS
# ---------------------------------------------------------

@router.get("/")
def list_orders(db: Session = Depends(get_db)):
    """
    Return all orders (admin use).
    """
    return db.query(Order).order_by(Order.id.desc()).all()


# ---------------------------------------------------------
# ADMIN: GET ORDER DETAILS
# ---------------------------------------------------------

@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Return order details including items.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return {
        "order": order,
        "items": items,
    }


# ---------------------------------------------------------
# ADMIN: GET ORDER ITEMS
# ---------------------------------------------------------

@router.get("/{order_id}/items")
def get_order_items(order_id: int, db: Session = Depends(get_db)):
    """
    Return only the order items.
    """
    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .all()
    )
    return items


# ---------------------------------------------------------
# ADMIN: GET ORDER PAYMENTS
# ---------------------------------------------------------

@router.get("/{order_id}/payments")
def get_order_payments(order_id: int, db: Session = Depends(get_db)):
    """
    Return all payments associated with this order.
    """
    payments = (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .order_by(Payment.id.desc())
        .all()
    )
    return payments
