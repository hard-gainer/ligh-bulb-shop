from typing import Any

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from order_service import crud
from order_service.db import get_db
from order_service.dto import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    to_order_response,
)
from order_service.exceptions import order_not_found

app = FastAPI()


@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)) -> Any:
    created_order = crud.create_order(db, order)
    return to_order_response(created_order)


@app.get("/api/v1/orders", response_model=list[OrderResponse])
async def get_all_orders_by_user(
    email: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> Any:
    found_orders = crud.get_orders(db, email=email, skip=skip, limit=limit)
    return [to_order_response(order) for order in found_orders]


@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: int, db: Session = Depends(get_db)) -> Any:
    found_order = crud.get_order_by_id(db, order_id)
    if not found_order:
        raise order_not_found()
    return to_order_response(found_order)


@app.patch("/api/v1/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)
) -> Any:
    updated_order = crud.update_order_status(db, order_id, payload.status)
    if not updated_order:
        raise order_not_found()
    return to_order_response(updated_order)
