from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from . import models, schemas, repository

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_user(db: Session, user: schemas.UserCreate):
    return repository.create_user(db=db, user=user)

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user(db: Session, username: str):
    return repository.get_user(db, username)

def get_user_by_email(db: Session, email: str):
    return repository.get_user_by_email(db, email)

def authenticate_user(db: Session, username: str, password: str):
    user = repository.get_user(db, username)
    if not user:
        return False
    if not repository.verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return False
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return False
    user = get_user(db, username=token_data.username)
    if user is None:
        return False
    return schemas.UserRead.model_validate(user)

def filter_users(db: Session,
        name: Optional[str] = None,
        surname: Optional[str] = None,
        email: Optional[str] = None):
    return repository.filter_users(db, name, surname, email)

