from pydantic import BaseModel
from enum import Enum

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

class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    user_level: UserLevel

    class Config:
        orm_mode = True