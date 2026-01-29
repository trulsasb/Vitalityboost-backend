from pydantic import BaseModel
from typing import List
from models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
