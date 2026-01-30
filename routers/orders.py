from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order
