from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


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
def create_user(user: User, db: Session = Depends(get_db)):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
