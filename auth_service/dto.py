from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from auth_service.schemas import User


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    role: UserRole


class UserUpdate(BaseModel):
    password: str = Field(min_length=6)


def to_user_response(user: User) -> UserResponse:
    return UserResponse(user_id=user.id, email=user.email, role=UserRole(user.role))
