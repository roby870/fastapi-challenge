from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, service
from .database import engine
from .repository import get_db
from typing import Optional


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.on_event("startup")
def startup_event():
    get_db()

@app.post("/create_user", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, token: str = Depends(oauth2_scheme),  db: Session = Depends(get_db)):
    current_user = service.get_current_user(db, token)
    if current_user.user_level != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_user = service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = service.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return service.create_user(db=db, user=user)


@app.get("/user/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = service.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/list_users/", response_model=list[schemas.UserRead])
def list_users(
    skip: int = Query(0, ge=0),  
    limit: int = Query(10, ge=1),  
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    current_user = service.get_current_user(db, token) 
    if current_user.user_level not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    query = service.filter_users(db, name, surname, email)
    users = query.offset(skip).limit(limit).all()
    return users