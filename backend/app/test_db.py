from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base

TEST_DATABASE_URL = "postgresql://postgres:password@db_test:5432/test_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def drop_db():
    Base.metadata.drop_all(bind=engine)