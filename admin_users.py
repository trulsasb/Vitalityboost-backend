from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from routers.auth import hash_password

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

PERMISSION_FIELDS = [
    "is_admin",
    "can_view_products",
    "can_edit_products",
    "can_view_orders",
    "can_view_payments",
    "can_manage_accounting",
]


class UserCreate(BaseModel):
    email: str
    password: str
    is_admin: bool = False
    can_view_products: bool = False
    can_edit_products: bool = False
    can_view_orders: bool = False
    can_view_payments: bool = False
    can_manage_accounting: bool = False


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    is_admin: bool | None = None
    can_view_products: bool | None = None
    can_edit_products: bool | None = None
    can_view_orders: bool | None = None
    can_view_payments: bool | None = None
    can_manage_accounting: bool | None = None


def _public(user: User) -> dict:
    data = {"id": user.id, "email": user.email, "created_at": user.created_at}
    for field in PERMISSION_FIELDS:
        data[field] = getattr(user, field)
    return data


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return [_public(u) for u in db.query(User).all()]


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _public(user)


@router.post("/")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        **{field: getattr(payload, field) for field in PERMISSION_FIELDS},
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _public(user)


@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    if "email" in data:
        user.email = data.pop("email")
    for field, value in data.items():
        setattr(user, field, value)
    if password:
        user.password_hash = hash_password(password)

    db.commit()
    db.refresh(user)
    return _public(user)
