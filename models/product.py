from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product

router = APIRouter(prefix="/admin/products", tags=["Admin – Products"])


# ---------------------------------------------------------
# LIST ALL PRODUCTS (ADMIN)
# ---------------------------------------------------------

@router.get("/")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.desc()).all()


# ---------------------------------------------------------
# GET SINGLE PRODUCT
# ---------------------------------------------------------

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ---------------------------------------------------------
# CREATE PRODUCT
# ---------------------------------------------------------

@router.post("/")
def create_product(
    name: str,
    price: float,
    stock: int = 0,
    active: bool = True,
    db: Session = Depends(get_db),
):
    if price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    product = Product(
        name=name,
        price=price,
        stock=stock,
        active=active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ---------------------------------------------------------
# UPDATE PRODUCT
# ---------------------------------------------------------

@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str | None = None,
    price: float | None = None,
    stock: int | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if price is not None and price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
    if active is not None:
        product.active = active

    db.commit()
    db.refresh(product)
    return product


# ---------------------------------------------------------
# DELETE PRODUCT
# ---------------------------------------------------------

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"status": "deleted", "product_id": product_id}
