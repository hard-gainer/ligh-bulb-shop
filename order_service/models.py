from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr


class OrderItem(BaseModel):
    product_id: int
    qty: int

class OrderCreate(BaseModel):
    phone: str
    email: EmailStr
    delivery_address: str
    items: List[OrderItem]

class OrderResponse(BaseModel):
    order_id: int
    status: str
    total_price: float
    created_at: datetime