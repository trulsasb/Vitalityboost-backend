from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.product import CartItem, Product
from models.order import Order, OrderItem, OrderStatus

router = APIRouter(prefix="/orders", tags=["Orders"])


class DirectOrderItem(BaseModel):
    product_id: int
    quantity: int


class DirectOrderRequest(BaseModel):
    items: list[DirectOrderItem]


# ---------------------------------------------------------
# CREATE ORDER DIRECTLY FROM CLIENT-SIDE CART (PUBLIC)
# ---------------------------------------------------------
# The storefront cart lives in the browser (not the backend CartItem
# table), so checkout posts the items straight from there rather than
# through the session-based /orders/{session_id} flow above.

@router.post("/direct")
def create_order_direct(payload: DirectOrderRequest, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    product_ids = [item.product_id for item in payload.items]
    products = {
        p.id: p
        for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    for item in payload.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

    total_amount = sum(products[item.product_id].price * item.quantity for item in payload.items)

    order = Order(total_amount=total_amount, status=OrderStatus.PENDING_PAYMENT)
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in payload.items:
        product = products[item.product_id]
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price,
        ))
        product.stock -= item.quantity

    db.commit()

    return {
        "order_id": order.id,
        "status": order.status.value,
        "total_amount": order.total_amount,
    }


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

    product_ids = [item.product_id for item in cart_items]
    products = {
        p.id: p
        for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    for item in cart_items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(
                status_code=400, detail=f"Product {item.product_id} not found"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}",
            )

    total_amount = sum(
        products[item.product_id].price * item.quantity for item in cart_items
    )

    order = Order(total_amount=total_amount, status=OrderStatus.PENDING_PAYMENT)
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart_items:
        product = products[item.product_id]
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price,
        )
        product.stock -= item.quantity
        db.add(order_item)

    db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).delete()

    db.commit()

    return {
        "order_id": order.id,
        "status": order.status.value,
        "total_amount": order.total_amount,
    }
