import os
from typing import Optional
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import User, Permission, UserPermission
from . import schemas


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_initial_data(db: Session):
    if db.query(User).count() == 0:
        john = User(username="John", name="John", surname="Doe", email="john.doe@example.com", password=get_password_hash("G*qE/6r$"))
        jane = User(username="Jane", name="Jane", surname="Doe", email="jane.doe@example.com", password=get_password_hash("G*qE/6r$"))
        db.add(john)
        db.add(jane)
        db.commit()
        db.refresh(john)
        db.refresh(jane)
        permission_admin = Permission(name="admin")
        permission_guest = Permission(name="guest")
        permission_user = Permission(name="user")
        db.add(permission_admin)  
        db.add(permission_guest)
        db.add(permission_user)
        db.commit()
        db.refresh(permission_admin)
        db.refresh(permission_guest)
        db.add(UserPermission(user_id=john.id, permission_id=permission_admin.id))
        db.add(UserPermission(user_id=jane.id, permission_id=permission_guest.id))
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
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    new_user = get_user(db, username = user.username)
    for permission_id in user.permissions:
        db.add(UserPermission(user_id=new_user.id, permission_id=permission_id))
    db.commit()
    return db_user

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def check_is_admin(db: Session, user: schemas.UserCheckPermisions):
    return db.query(UserPermission).filter(UserPermission.user_id == user.id, UserPermission.permission_id == 1).first()

def check_is_admin_or_user(db: Session, user: schemas.UserCheckPermisions):
    return db.query(UserPermission).filter(UserPermission.user_id == user.id, UserPermission.permission_id.in_([1, 3])).first()

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