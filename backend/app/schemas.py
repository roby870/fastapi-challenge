from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserLevel(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    user_level: UserLevel
    password: str

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    user_level: UserLevel

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None