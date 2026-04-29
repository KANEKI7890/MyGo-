from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BandPosition, UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=UserRole.MEMBER,
        nullable=False,
    )
    band_position: Mapped[BandPosition] = mapped_column(
        Enum(
            BandPosition,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    practices = relationship("PracticeRecord", back_populates="user", cascade="all, delete-orphan")
    enrollments = relationship("EventEnrollment", back_populates="user", cascade="all, delete-orphan")
