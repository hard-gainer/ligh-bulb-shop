from fastapi import APIRouter, Depends, HTTPException
from models import UserRegister, Token

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

def get_current_user(token: str = "dummy_token"):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user_id": 1, "email": "user@example.com"}

@auth_router.post("/register", response_model=Token)
async def register(user: UserRegister):
    return {"access_token": "new_jwt_token", "token_type": "bearer"}

@auth_router.post("/login", response_model=Token)
async def login(login_data: dict):
    return {"access_token": "valid_jwt_token", "token_type": "bearer"}