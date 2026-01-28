from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product, CartItem
from schemas.cart import CartItemCreate

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.post("/add")
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db)):
    # Finn produktet
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Sjekk om varen allerede ligger i cart for denne session_id
    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.session_id == item.session_id,
            CartItem.product_id == item.product_id
        )
        .first()
    )

    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    # Opprett nytt cart-item
    new_item = CartItem(
        session_id=item.session_id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/{session_id}")
def get_cart(session_id: str, db: Session = Depends(get_db)):
    items = db.query(CartItem).filter(CartItem.session_id == session_id).all()
    return items


@router.delete("/{session_id}/{product_id}")
def remove_from_cart(session_id: str, product_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(CCartItem)
        .filter(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"detail": "Item removed"}
