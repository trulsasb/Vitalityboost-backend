from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.orm import Session

from database import get_db
from models.discount import DiscountRedemption
from models.product import CartItem, Product
from models.order import Order, OrderItem, OrderStatus
from services.discount_service import DiscountCheckItem, check_discount_code, try_redeem_discount_code
from services.email_service import EmailService
from utils.validators import validate_email

router = APIRouter(prefix="/orders", tags=["Orders"])


def _try_reserve_stock(db: Session, product_id: int, quantity: int) -> bool:
    """Atomically decrements stock, but only if enough is still available —
    a single conditional UPDATE re-checks the live row instead of trusting
    the Python-side read from a few lines earlier, which is what lets two
    concurrent checkouts both pass validation and both decrement the same
    unit. Returns False if a concurrent order already claimed it."""

    result = db.execute(
        update(Product)
        .where(Product.id == product_id, Product.stock >= quantity)
        .values(stock=Product.stock - quantity)
    )
    return result.rowcount == 1


class DirectOrderItem(BaseModel):
    product_id: int
    quantity: int


class DirectOrderRequest(BaseModel):
    items: list[DirectOrderItem]
    customer_name: str
    customer_email: str
    shipping_address: str
    shipping_zip: str
    shipping_city: str
    discount_code: str | None = None


# ---------------------------------------------------------
# CREATE ORDER DIRECTLY FROM CLIENT-SIDE CART (PUBLIC)
# ---------------------------------------------------------
# The storefront cart lives in the browser (not the backend CartItem
# table), so checkout posts the items straight from there rather than
# through the session-based /orders/{session_id} flow above.

@router.post("/direct")
async def create_order_direct(payload: DirectOrderRequest, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    validate_email(payload.customer_email)
    for field_name, value in [
        ("customer_name", payload.customer_name),
        ("shipping_address", payload.shipping_address),
        ("shipping_zip", payload.shipping_zip),
        ("shipping_city", payload.shipping_city),
    ]:
        if not value or not value.strip():
            raise HTTPException(status_code=400, detail=f"{field_name} is required")

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

    subtotal = sum(products[item.product_id].price * item.quantity for item in payload.items)

    discount_amount = 0.0
    discount_result = None
    if payload.discount_code:
        check_items = [
            DiscountCheckItem(product_id=item.product_id, quantity=item.quantity, price=products[item.product_id].price)
            for item in payload.items
        ]
        discount_result = check_discount_code(db, payload.discount_code, check_items, payload.customer_email)
        if not discount_result.valid:
            raise HTTPException(status_code=400, detail=discount_result.message)
        discount_amount = discount_result.discount_amount

    total_amount = max(0.0, subtotal - discount_amount)

    order = Order(
        total_amount=total_amount,
        status=OrderStatus.PENDING_PAYMENT,
        customer_name=payload.customer_name.strip(),
        customer_email=payload.customer_email.strip(),
        shipping_address=payload.shipping_address.strip(),
        shipping_zip=payload.shipping_zip.strip(),
        shipping_city=payload.shipping_city.strip(),
    )
    db.add(order)
    db.flush()  # assigns order.id without committing, in case reservation below fails

    for item in payload.items:
        product = products[item.product_id]
        if not _try_reserve_stock(db, item.product_id, item.quantity):
            db.rollback()
            raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price,
        ))

    if discount_result and discount_result.valid and discount_result.discount_code:
        if not try_redeem_discount_code(db, discount_result.discount_code.id):
            db.rollback()
            raise HTTPException(status_code=409, detail="Discount code was just used up")
        db.add(DiscountRedemption(
            discount_code_id=discount_result.discount_code.id,
            order_id=order.id,
            amount=discount_amount,
        ))

    db.commit()
    db.refresh(order)

    try:
        await EmailService().send_order_confirmation(
            to_email=order.customer_email,
            subject=f"Vitalityboost — bekreftelse på ordre #{order.id}",
            body=f"Takk for din bestilling! Ordre #{order.id} på {order.total_amount} kr er mottatt.",
        )
    except Exception:
        pass  # Confirmation email is best-effort; it must never block checkout.

    return {
        "order_id": order.id,
        "status": order.status.value,
        "total_amount": order.total_amount,
        "discount_amount": discount_amount,
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
    db.flush()  # assigns order.id without committing, in case reservation below fails

    for item in cart_items:
        product = products[item.product_id]
        if not _try_reserve_stock(db, item.product_id, item.quantity):
            db.rollback()
            raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price,
        )
        db.add(order_item)

    db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).delete()

    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "status": order.status.value,
        "total_amount": order.total_amount,
    }
