from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import LoginRequest, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=UserRole.MEMBER,
        band_position=payload.band_position,
        bio=payload.bio,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> Token:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return Token(access_token=create_access_token(str(user.id)))
