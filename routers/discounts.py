from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from services.discount_service import DiscountCheckItem, check_discount_code

router = APIRouter(prefix="/discounts", tags=["Discounts"])


class ValidateItem(BaseModel):
    product_id: int
    quantity: int


class ValidateDiscountRequest(BaseModel):
    code: str
    items: list[ValidateItem]
    customer_email: str | None = None


@router.post("/validate")
def validate_discount(payload: ValidateDiscountRequest, db: Session = Depends(get_db)):
    # Prices are looked up server-side from the database — never trust a
    # client-supplied price when computing a discount amount.
    product_ids = [item.product_id for item in payload.items]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}

    check_items = [
        DiscountCheckItem(product_id=item.product_id, quantity=item.quantity, price=products[item.product_id].price)
        for item in payload.items
        if item.product_id in products
    ]

    result = check_discount_code(db, payload.code, check_items, payload.customer_email)

    return {
        "valid": result.valid,
        "message": result.message,
        "discount_amount": result.discount_amount,
    }
