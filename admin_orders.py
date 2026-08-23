from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderItem, OrderStatus
from models.product import Product
from routers.auth import get_current_admin, require_permission

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

_can_view = [Depends(require_permission("can_view_orders"))]
_owner_only = [Depends(get_current_admin)]


@router.get("/", dependencies=_can_view)
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{order_id}", dependencies=_can_view)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", dependencies=_owner_only)
def create_order(db: Session = Depends(get_db)):
    order = Order()
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}/status", dependencies=_owner_only)
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/items", dependencies=_owner_only)
def add_item(order_id: int, product_id: int, quantity: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price_at_purchase=product.price,
    )
    db.add(item)
    order.total_amount += product.price * quantity
    db.commit()
    db.refresh(item)
    return item
