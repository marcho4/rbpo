import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth import AuthService
from app.crud.crud import UserCRUD
from app.db.database import get_db
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter(tags=["authentication"])
auth_logger = logging.getLogger("auth_logger")
auth_logger.setLevel(logging.INFO)
auth_logger.addHandler(logging.StreamHandler())


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if UserCRUD.get_user_by_username(db, user.username):
        auth_logger.info(f"User already exists: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )

    if UserCRUD.get_user_by_email(db, user.email):
        auth_logger.info(f"User already exists: {user.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")

    db_user = UserCRUD.create_user(db, user)
    auth_logger.info(f"User created: {db_user.id}")
    return db_user


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        auth_logger.info(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(data={"sub": user.username})
    auth_logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}
