from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from .. import models, database
from ..utils.security import create_jwt_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    password: str
    is_admin: bool = True


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create_admin")
def create_admin(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed, is_admin=user.is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Admin created", "user_id": new_user.id}


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token(user.email)
    return {"access_token": token, "token_type": "bearer"}
