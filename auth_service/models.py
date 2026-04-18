from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    login: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"