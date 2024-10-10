from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

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