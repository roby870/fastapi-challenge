from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum as PyEnum

class UserLevel(PyEnum):
    admin = "admin"
    user = "user"
    guest = "guest"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    user_level = Column(Enum(UserLevel), default=UserLevel.user)
    password = Column(String)