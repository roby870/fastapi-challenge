from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum
from typing import Optional
import re

class UserLevel(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class UserCreate(BaseModel):
    username: str
    name: str
    surname: str
    email: str
    user_level: UserLevel
    password: str

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
    username: str
    name: str
    surname: str
    email: EmailStr
    user_level: UserLevel

    class Config:
        from_attributes = True
        use_enum_values = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None