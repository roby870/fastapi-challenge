import re
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List


class UserCreate(BaseModel):
    username: str = Field(max_length=32)
    name: str = Field(max_length=32)
    surname: str = Field(max_length=32)
    email: EmailStr 
    permissions: List[int]
    password: str = Field(max_length=32)

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    username: str = Field(max_length=32)
    name: str = Field(max_length=32)
    surname: str = Field(max_length=32)
    email: EmailStr

    class Config:
        from_attributes = True

class UserCheckPermisions(BaseModel):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class Permission(BaseModel):
    id: int
    name: str  

    class Config:
        from_attributes = True