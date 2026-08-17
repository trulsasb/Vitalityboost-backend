from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.discount import DiscountCode
from models.product import Product
from routers.auth import require_permission

router = APIRouter(prefix="/admin/discounts", tags=["Admin Discounts"])

_can_view = [Depends(require_permission("can_view_products"))]
_can_edit = [Depends(require_permission("can_edit_products"))]


class DiscountCreate(BaseModel):
    code: str
    discount_type: Literal["percentage", "fixed"]
    value: float
    customer_email: str | None = None
    product_id: int | None = None
    active: bool = True
    expires_at: datetime | None = None
    max_uses: int | None = None


class DiscountUpdate(BaseModel):
    discount_type: Literal["percentage", "fixed"] | None = None
    value: float | None = None
    customer_email: str | None = None
    product_id: int | None = None
    active: bool | None = None
    expires_at: datetime | None = None
    max_uses: int | None = None


def _validate_value(discount_type: str, value: float):
    if value <= 0:
        raise HTTPException(status_code=400, detail="Verdi må være positiv")
    if discount_type == "percentage" and value > 100:
        raise HTTPException(status_code=400, detail="Prosentrabatt kan ikke være over 100%")


@router.get("/", dependencies=_can_view)
def list_discounts(db: Session = Depends(get_db)):
    return db.query(DiscountCode).order_by(DiscountCode.created_at.desc()).all()


@router.post("/", dependencies=_can_edit)
def create_discount(payload: DiscountCreate, db: Session = Depends(get_db)):
    code = payload.code.strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="Kode kan ikke være tom")

    _validate_value(payload.discount_type, payload.value)

    if payload.product_id is not None:
        product = db.query(Product).filter(Product.id == payload.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail="Fant ikke produktet")

    if db.query(DiscountCode).filter(DiscountCode.code == code).first():
        raise HTTPException(status_code=409, detail="Denne koden finnes allerede")

    discount = DiscountCode(
        code=code,
        discount_type=payload.discount_type,
        value=payload.value,
        customer_email=payload.customer_email.strip().lower() if payload.customer_email else None,
        product_id=payload.product_id,
        active=payload.active,
        expires_at=payload.expires_at,
        max_uses=payload.max_uses,
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


@router.put("/{discount_id}", dependencies=_can_edit)
def update_discount(discount_id: int, payload: DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(DiscountCode).filter(DiscountCode.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Fant ikke rabattkoden")

    updates = payload.model_dump(exclude_unset=True)

    if "product_id" in updates and updates["product_id"] is not None:
        product = db.query(Product).filter(Product.id == updates["product_id"]).first()
        if not product:
            raise HTTPException(status_code=400, detail="Fant ikke produktet")

    new_type = updates.get("discount_type", discount.discount_type)
    new_value = updates.get("value", discount.value)
    if "discount_type" in updates or "value" in updates:
        _validate_value(new_type, new_value)

    if "customer_email" in updates and updates["customer_email"]:
        updates["customer_email"] = updates["customer_email"].strip().lower()

    for field, value in updates.items():
        setattr(discount, field, value)

    db.commit()
    db.refresh(discount)
    return discount


@router.delete("/{discount_id}", dependencies=_can_edit)
def delete_discount(discount_id: int, db: Session = Depends(get_db)):
    discount = db.query(DiscountCode).filter(DiscountCode.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Fant ikke rabattkoden")

    db.delete(discount)
    db.commit()
    return {"status": "deleted", "id": discount_id}
