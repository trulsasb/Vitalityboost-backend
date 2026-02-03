from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/")
def create_user(email: str, name: str, password_hash: str, db: Session = Depends(get_db)):
    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}")
def update_user(user_id: int, email: str, name: str, password_hash: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = email
    user.name = name
    user.password_hash = password_hash

    db.commit()
    db.refresh(user)
    return user
