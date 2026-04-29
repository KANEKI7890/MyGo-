from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine
from app.models import Event, EventEnrollment, PracticeRecord, User  # noqa: F401
from app.models.enums import BandPosition, UserRole


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_admin(db: Session) -> None:
    settings = get_settings()
    existing_admin = db.scalar(select(User).where(User.email == settings.admin_email))
    if existing_admin:
        return

    admin = User(
        email=settings.admin_email,
        username=settings.admin_username,
        hashed_password=get_password_hash(settings.admin_password),
        role=UserRole.ADMIN,
        band_position=BandPosition(settings.admin_band_position),
        bio="System generated administrator account.",
    )
    db.add(admin)
    db.commit()
