from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.product import CartItem, Product
from routers.auth import require_permission
from utils.validators import validate_amount

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

_can_view = [Depends(require_permission("can_view_products"))]
_can_edit = [Depends(require_permission("can_edit_products"))]


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    category: str | None = None
    image: str | None = None
    active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category: str | None = None
    image: str | None = None
    active: bool | None = None


@router.get("/", dependencies=_can_view)
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/{product_id}", dependencies=_can_view)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", dependencies=_can_edit)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    validate_amount(payload.price)
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", dependencies=_can_edit)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.price is not None:
        validate_amount(payload.price)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", dependencies=_can_edit)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Clear any leftover cart_items referencing this product first — that
    # table has a foreign key to products and isn't cleaned up by the
    # current (localStorage-based) checkout flow, so stale rows can exist.
    db.query(CartItem).filter(CartItem.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"status": "deleted", "id": product_id}
