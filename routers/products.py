from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Product
from pydantic import BaseModel

router = APIRouter()


# -----------------------------
#   SCHEMAS
# -----------------------------
class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    active: bool

    class Config:
        orm_mode = True


class ProductIn(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    active: bool = True


# -----------------------------
#   ROUTES
# -----------------------------
@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.active == True).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut)
def create_product(data: ProductIn, db: Session = Depends(get_db)):
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
