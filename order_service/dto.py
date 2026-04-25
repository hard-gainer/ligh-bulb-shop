from datetime import datetime
from typing import List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from order_service.schemas import Order


class OrderStatus(Enum):
    CREATED = "CREATED"
    SHIPPED = "SHIPPED"


class OrderItemCreate(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class OrderCreate(BaseModel):
    phone: str
    email: EmailStr
    delivery_address: str
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    qty: int
    unit_price: float


class OrderResponse(BaseModel):
    order_id: int
    status: str
    total_price: float
    created_at: datetime
    phone: str
    email: EmailStr
    delivery_address: str
    items: List[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: str


def to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        order_id=order.id,
        status=order.status,
        total_price=order.total_price,
        created_at=order.created_at,
        phone=order.phone,
        email=order.email,
        delivery_address=order.delivery_address,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                qty=item.qty,
                unit_price=item.unit_price,
            )
            for item in order.items
        ],
    )
