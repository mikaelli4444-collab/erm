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

class CompanySchema(BaseModel):
    name: str
    legal_name: str
    tax_id: str
    email: EmailStr
    plan: Literal["basico", "pro", "enterprise"]