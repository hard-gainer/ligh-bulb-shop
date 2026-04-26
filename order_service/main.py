import importlib
from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth_service.auth import (
    AuthUser,
    attach_auth_user_to_request,
    get_current_user,
    require_admin,
)
from order_service import crud
from order_service.db import Base, engine, get_db
from order_service.dto import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    to_order_response,
)
from order_service.exceptions import order_access_forbidden, order_not_found


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    importlib.import_module("order_service.schemas")
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def authentication_middleware(request: Request, call_next: Any) -> Any:
    try:
        attach_auth_user_to_request(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)


@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    order_to_create = order.model_copy(update={"email": current_user.email})
    created_order = crud.create_order(db, order_to_create)
    return to_order_response(created_order)


@app.get("/api/v1/orders", response_model=list[OrderResponse])
async def get_all_orders_by_user(
    email: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    if current_user.role != "ADMIN":
        email = current_user.email

    found_orders = crud.get_orders(db, email=email, skip=skip, limit=limit)
    return [to_order_response(order) for order in found_orders]


@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: int,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    found_order = crud.get_order_by_id(db, order_id)
    if not found_order:
        raise order_not_found()

    if current_user.role != "ADMIN" and found_order.email != current_user.email:
        raise order_access_forbidden()

    return to_order_response(found_order)


@app.patch("/api/v1/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    _: AuthUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Any:
    updated_order = crud.update_order_status(db, order_id, payload.status)
    if not updated_order:
        raise order_not_found()
    return to_order_response(updated_order)
