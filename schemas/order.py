from pydantic import BaseModel
from typing import List

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: int

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    total_amount: int
    status: str
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True
