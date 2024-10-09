from fastapi import FastAPI, HTTPException, Depends, status
from fastapi import Form
from sqlalchemy.orm import Session
from . import models, schemas, service
from .database import engine, get_db
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30

class OAuth2EmailPasswordRequestForm:
    def __init__(
        self,
        email: str = Form(...), 
        password: str = Form(...)
    ):
        self.email = email
        self.password = password

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/create_user", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, token: schemas.Token,  db: Session = Depends(get_db)):
    current_user = service.get_current_user(db, token.access_token)
    if current_user.user_level != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_user = service.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_user(db=db, user=user)


@app.get("/user/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = service.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2EmailPasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = service.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}