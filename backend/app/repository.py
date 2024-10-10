import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import User
from . import schemas
from typing import Optional
from passlib.context import CryptContext

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_initial_data(db: Session):
    if db.query(User).count() == 0:
        users = [
            User(username="John", name="John", surname="Doe", email="john.doe@example.com", user_level="admin", password=get_password_hash("securepassword")),
            User(username="Jane", name="Jane", surname="Doe", email="jane.doe@example.com", user_level="user", password=get_password_hash("securepassword")),
        ]
        db.bulk_save_objects(users)  
        db.commit()

def get_db():
    db = SessionLocal()
    try:
        create_initial_data(db)
        yield db
    finally:
        db.close()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        name=user.name,
        surname=user.surname,
        email=user.email,
        user_level=user.user_level,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def filter_users(db: Session,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None):
    query = db.query(User)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if surname:
        query = query.filter(User.surname.ilike(f"%{surname}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    return query