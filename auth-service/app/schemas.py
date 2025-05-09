from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    name: str
    login: str
    phone: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    user_id: int
    email: Optional[EmailStr] = None
    name: str
    login: str
    phone: Optional[str] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    login: str
    password: str