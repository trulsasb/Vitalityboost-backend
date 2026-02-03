from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from routers.auth import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", dependencies=[Depends(get_current_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}", dependencies=[Depends(get_current_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
