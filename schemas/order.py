from pydantic import BaseModel
from typing import List
from enum import Enum


# -----------------------------
#   ENUM (MATCHES DB MODEL)
# -----------------------------
class OrderStatus(str, Enum):
    pending_payment = "pending_payment"
    paid = "paid"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"


# -----------------------------
#   CREATE SCHEMAS
# -----------------------------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


# -----------------------------
#   RESPONSE SCHEMAS
# -----------------------------
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    total_amount: float | None = None
    status: OrderStatus
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True


# -----------------------------
#   UPDATE STATUS SCHEMA
# -----------------------------
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
