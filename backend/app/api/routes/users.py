from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.enums import BandPosition
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


@router.get("/positions")
def list_positions() -> list[dict[str, str]]:
    labels = {
        BandPosition.VOCAL: "主唱 / Vocal",
        BandPosition.GUITAR: "吉他 / Guitar",
        BandPosition.BASS: "贝斯 / Bass",
        BandPosition.DRUM: "鼓 / Drum",
        BandPosition.KEYBOARD: "键盘 / Keyboard",
    }
    return [{"value": position.value, "label": labels[position]} for position in BandPosition]
