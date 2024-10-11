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
    """
    Create a new user in the system.

    This endpoint allows an admin to create a new user. It verifies that the 
    requester has admin privileges and checks if the provided email and username are 
    already registered. If the checks pass, a new user is created in the database.

    Parameters:
    - user (schemas.UserCreate): The user data required to create a new user, 
      including username and email.
    - token (str): The OAuth2 token for authentication, used to identify the 
      current user.
    - db (Session): The database session for executing database operations.

    Returns:
    - schemas.UserRead: The created user's information.

    Raises:
    - HTTPException: If the current user is not authenticated or not an admin.
    - HTTPException: If the email is already registered.
    - HTTPException: If the username is already registered.
    """
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
    """
    Authenticate a user and return an access token.

    This endpoint allows a user to log in by providing their username and password. 
    If the credentials are valid, an access token is generated and returned for 
    subsequent authenticated requests.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): The form data containing the username 
      and password for authentication.
    - db (Session): The database session for executing database operations.

    Returns:
    - schemas.Token: A dictionary containing the access token and its type (bearer).

    Raises:
    - HTTPException: If the credentials are invalid or the user cannot be authenticated.
    """
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
    """
    Retrieve a list of users from the system.

    This endpoint allows an authenticated user (with admin or user privileges) to 
    retrieve a paginated list of users. The list can be filtered based on optional 
    query parameters for name, surname, and email.

    Parameters:
    - skip (int): The number of users to skip in the result set. Defaults to 0. Must be non-negative.
    - limit (int): The maximum number of users to return. Defaults to 10. Must be at least 1.
    - name (Optional[str]): Filter users by their name.
    - surname (Optional[str]): Filter users by their surname.
    - email (Optional[str]): Filter users by their email address.
    - db (Session): The database session for executing database operations.
    - token (str): The OAuth2 token for authentication, used to identify the 
      current user.

    Returns:
    - list[schemas.UserRead]: A list of users matching the specified criteria.

    Raises:
    - HTTPException: If the current user is not authenticated or not authorized to access the user list.
    """
    current_user = service.get_current_user(db, token) 
    if not current_user:
        raise CustomExceptions.get_credentials_exception()
    if current_user.user_level not in ["admin", "user"]:
        raise CustomExceptions.get_not_authorized_exception()
    query = service.filter_users(db, name, surname, email)
    users = query.offset(skip).limit(limit).all()
    return users


@app.get("/counters/")
def get_counters(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Retrieve the counters for API call usage.

    This endpoint allows an administrator to access counters that track the number 
    of times specific API calls have been made, such as user creation and user 
    listing. Access to this endpoint is restricted to users with admin privileges.

    Parameters:
    - db (Session): The database session for executing database operations.
    - token (str): The OAuth2 token for authentication, used to identify the 
      current user.

    Returns:
    - dict: A dictionary containing counters for various API calls, including:
        - "create_user_calls": The number of times the create user endpoint has been called.
        - "list_users_calls": The number of times the list users endpoint has been called.

    Raises:
    - HTTPException: If the current user is not authenticated or not authorized.
    """
    current_user = service.get_current_user(db, token)
    if not current_user:
        raise CustomExceptions.get_credentials_exception()
    if current_user.user_level != "admin":
        raise CustomExceptions.get_not_authorized_exception()
    return {
        "create_user_calls": create_user_counter,
        "list_users_calls": list_users_counter
    }