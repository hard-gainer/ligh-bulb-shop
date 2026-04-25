import os
import time
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, Request
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

ACCESS_TOKEN_TTL_SECONDS = int(os.getenv("AUTH_ACCESS_TOKEN_TTL", "3600"))
auth_secret_env = os.getenv("AUTH_SECRET")
JWT_ALGORITHM = "HS256"

if not auth_secret_env:
    raise ValueError("AUTH_SECRET must be set")

AUTH_SECRET: str = auth_secret_env


@dataclass
class AuthUser:
    user_id: int
    email: str
    role: str


def create_access_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": int(time.time()) + ACCESS_TOKEN_TTL_SECONDS,
    }
    return jwt.encode(payload, AUTH_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> AuthUser:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            AUTH_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_id_raw = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")
    if not user_id_raw or not isinstance(email, str) or not isinstance(role, str):
        raise HTTPException(status_code=401, detail="Invalid access token")

    try:
        user_id = int(user_id_raw)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return AuthUser(user_id=user_id, email=email, role=role)


def attach_auth_user_to_request(request: Request) -> None:
    auth_header = request.headers.get("Authorization")
    request.state.auth_user = None

    if not auth_header:
        return

    try:
        scheme, token = auth_header.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    request.state.auth_user = decode_access_token(token)


def get_current_user(request: Request) -> AuthUser:
    auth_user = getattr(request.state, "auth_user", None)
    if auth_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return auth_user


def require_admin(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user
