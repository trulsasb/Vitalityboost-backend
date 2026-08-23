from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.category import Category
from routers.auth import require_permission

router = APIRouter(prefix="/admin/categories", tags=["Admin Categories"])

_can_view = [Depends(require_permission("can_view_products"))]
_can_edit = [Depends(require_permission("can_edit_products"))]


class CategoryCreate(BaseModel):
    name: str


@router.get("/", dependencies=_can_view)
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


@router.post("/", dependencies=_can_edit)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name is required")

    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        return existing

    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
