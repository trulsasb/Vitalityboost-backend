from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.product import CartItem, Product

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/{session_id}")
def get_cart(session_id: str, db: Session = Depends(get_db)):
    return (
        db.query(CartItem)
        .filter(CartItem.session_id == session_id)
        .all()
    )


@router.post("/{session_id}/add/{product_id}")
def add_to_cart(session_id: str, product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = (
        db.query(CartItem)
        .filter(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id,
        )
        .first()
    )

    if item:
        item.quantity += 1
    else:
        item = CartItem(
            session_id=session_id,
            product_id=product_id,
            quantity=1,
        )
        db.add(item)

    db.commit()
    db.refresh(item)
    return item


@router.post("/{session_id}/remove/{product_id}")
def remove_from_cart(session_id: str, product_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(CartItem)
        .filter(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    if item.quantity > 1:
        item.quantity -= 1
        db.commit()
        db.refresh(item)
        return item

    db.delete(item)
    db.commit()
    return {"detail": "Item removed"}
