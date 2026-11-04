from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models import UserRole

# Base user fields
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.EMPLOYEE

# DTO used for incoming registration payload
class UserCreate(UserBase):
    password: str

# DTO returned to client (excludes password hash)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Token response DTO
class Token(BaseModel):
    access_token: str
    token_type: str

# Payload decoded from JWT
class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None