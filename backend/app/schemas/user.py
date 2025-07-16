from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    google_id: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_first_login: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    google_id: str
    is_first_login: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    is_first_login: bool