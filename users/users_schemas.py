from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr 
    password: str = Field(..., min_length=8)
    fullname: str = Field(..., min_length=3, max_length=50)

    class Config:
        from_attributes = True

class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50) 
    password: str = Field(..., min_length=8)
    class Config:
        from_attributes = True

class ContactSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=6, max_length=20)
    contact_type: Literal["client", "architect"]
    address: str = Field(..., min_length=5, max_length=255)

    class Config:
        from_attributes = True

