import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request

ACCESS_TOKEN_TTL_SECONDS = int(os.getenv("AUTH_ACCESS_TOKEN_TTL", "3600"))
auth_secret_env = os.getenv("AUTH_SECRET")

if not auth_secret_env:
    raise ValueError("AUTH_SECRET must be set")

AUTH_SECRET: str = auth_secret_env


@dataclass
class AuthUser:
    user_id: int
    email: str
    role: str


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _sign(unsigned_token: str) -> str:
    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        unsigned_token.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(signature)


def create_access_token(user_id: int, email: str, role: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": int(time.time()) + ACCESS_TOKEN_TTL_SECONDS,
    }

    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64url_encode(
        json.dumps(payload, separators=(",", ":")).encode()
    )
    unsigned_token = f"{encoded_header}.{encoded_payload}"
    signature = _sign(unsigned_token)
    return f"{unsigned_token}.{signature}"


def decode_access_token(token: str) -> AuthUser:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid access token")

    encoded_header, encoded_payload, encoded_signature = parts
    unsigned_token = f"{encoded_header}.{encoded_payload}"
    expected_signature = _sign(unsigned_token)
    if not hmac.compare_digest(encoded_signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid access token")

    try:
        payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid access token")

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise HTTPException(status_code=401, detail="Access token expired")

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
