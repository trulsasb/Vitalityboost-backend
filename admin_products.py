from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])


@router.get("/")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/")
def create_product(name: str, description: str, price: float, stock: int, db: Session = Depends(get_db)):
    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}")
def update_product(product_id: int, name: str, description: str, price: float, stock: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = name
    product.description = description
    product.price = price
    product.stock = stock

    db.commit()
    db.refresh(product)
    return product
