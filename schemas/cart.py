from pydantic import BaseModel

class CartItemCreate(BaseModel):
    session_id: str
    product_id: int
    quantity: int
