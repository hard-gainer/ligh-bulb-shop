import importlib
from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth_service import crud
from auth_service.db import Base, engine, get_db
from auth_service.dto import (
    RefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
    to_user_response,
)
from auth_service.exceptions import (
    invalid_credentials,
    invalid_refresh_token,
    user_not_found,
)
from auth_service.auth import (
    AuthUser,
    attach_auth_user_to_request,
    create_access_token,
    get_current_user,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    importlib.import_module("auth_service.schemas")
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


@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register(payload: UserRegister, db: Session = Depends(get_db)) -> Any:
    created_user = crud.create_user(db, payload)
    access_token = create_access_token(
        user_id=created_user.id,
        email=created_user.email,
        role=created_user.role,
    )
    refresh_token = crud.create_refresh_token(db, created_user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Session = Depends(get_db)) -> Any:
    found_user = crud.authenticate_user(db, payload.email, payload.password)
    if not found_user:
        raise invalid_credentials()

    access_token = create_access_token(
        user_id=found_user.id,
        email=found_user.email,
        role=found_user.role,
    )
    refresh_token = crud.create_refresh_token(db, found_user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> Any:
    stored_refresh_token = crud.get_valid_refresh_token(db, payload.refresh_token)
    if not stored_refresh_token:
        raise invalid_refresh_token()

    found_user = crud.get_user_by_id(db, stored_refresh_token.user_id)
    if not found_user:
        raise invalid_credentials()

    crud.revoke_refresh_token(db, stored_refresh_token)
    new_access_token = create_access_token(
        user_id=found_user.id,
        email=found_user.email,
        role=found_user.role,
    )
    new_refresh_token = crud.create_refresh_token(db, found_user.id)
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_me(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    found_user = crud.get_user_by_id(db, current_user.user_id)
    if not found_user:
        raise user_not_found()
    return to_user_response(found_user)


@app.put("/api/v1/users/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    found_user = crud.get_user_by_id(db, current_user.user_id)
    if not found_user:
        raise user_not_found()

    updated_user = crud.update_user(db, found_user, payload)
    return to_user_response(updated_user)
