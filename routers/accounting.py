from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import models
import database

from pydantic import BaseModel

router = APIRouter()

class CartItemIn(BaseModel):
    product_id: int
    quantity: int = 1
    session_id: str

class CartItemOut(BaseModel):
    id: int
    session_id: str
    quantity: int
    product_id: int
    class Config:
        orm_mode = True


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[CartItemOut])
def get_cart(session_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.CartItem).filter(models.CartItem.session_id == session_id).all()


@router.post("/", response_model=CartItemOut)
def add_to_cart(item: CartItemIn, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.session_id == item.session_id,
        models.CartItem.product_id == item.product_id
    ).first()
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = models.CartItem(**item.dict())
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed"}
