from fastapi import FastAPI, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, service
from .database import engine
from .repository import get_db
from typing import Optional
from .exceptions import CustomExceptions
import logging
import threading
import time


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

create_user_counter = 0
list_users_counter = 0
background_counter = 0


logging.basicConfig(filename="app/app.log",  
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
    filemode='a')
logger = logging.getLogger(__name__)


def increment_background_counter():
    global background_counter
    while True:
        time.sleep(300)  
        background_counter += 1
        logging.info(f"Background counter incremented to {background_counter}")


@app.on_event("startup")
def startup_event():
    get_db()
    threading.Thread(target=increment_background_counter, daemon=True).start()


def increment_create_user_counter():
    logger.info("POST /create_user")
    global create_user_counter
    create_user_counter += 1


def increment_list_users_counter():
    logger.info("GET /list_users")
    global list_users_counter
    list_users_counter += 1


@app.post("/create_user", response_model=schemas.UserRead, dependencies=[Depends(increment_create_user_counter)])
def create_user(user: schemas.UserCreate, token: str = Depends(oauth2_scheme),  db: Session = Depends(get_db)):
    current_user = service.get_current_user(db, token)
    if not current_user:
        raise CustomExceptions.get_credentials_exception()
    if current_user.user_level != "admin":
        raise CustomExceptions.get_not_authorized_exception()
    db_user = service.get_user_by_email(db, email=user.email)
    if db_user:
        raise CustomExceptions.get_bad_request_exception(detail="Email already registered")
    db_user = service.get_user(db, username=user.username)
    if db_user:
        raise CustomExceptions.get_bad_request_exception(detail="Username already registered")
    return service.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise CustomExceptions.get_credentials_exception()
    access_token = service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/list_users/", response_model=list[schemas.UserRead], dependencies=[Depends(increment_list_users_counter)])
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
        raise CustomExceptions.get_not_authorized_exception()
    query = service.filter_users(db, name, surname, email)
    users = query.offset(skip).limit(limit).all()
    return users

#I asume only an admin have permisson
@app.get("/counters/")
def get_counters(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = service.get_current_user(db, token)
    if current_user.user_level != "admin":
        raise CustomExceptions.get_not_authorized_exception()
    return {
        "create_user_calls": create_user_counter,
        "list_users_calls": list_users_counter
    }