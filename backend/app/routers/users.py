from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas import UserResponse, UserCreate
from app.database import users_collection, get_next_id
from app.utils.logger import logger
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def user_doc_to_response(doc: dict) -> dict:
    """Convert MongoDB document to response format (strip _id and password)."""
    doc.pop("_id", None)
    doc.pop("password", None)
    return doc


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    db_user = users_collection.find_one({"username": user.username})
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    user_doc = {
        "id": get_next_id("users"),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password": hash_password(user.password),
        "is_active": True,
    }
    users_collection.insert_one(user_doc)
    return user_doc_to_response(user_doc)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency: decode JWT and return the current user document."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return user_doc_to_response(current_user)
