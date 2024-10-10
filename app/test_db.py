import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def drop_db():
    Base.metadata.drop_all(bind=engine)