from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class CurrentUser(UserBase):
    id: int

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Login(UserBase):
    password: str