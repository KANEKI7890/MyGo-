from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BandPosition, EnrollmentStatus, EventStatus


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(160), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EventStatus] = mapped_column(
        Enum(
            EventStatus,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=EventStatus.OPEN,
        nullable=False,
    )
    required_vocal: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_guitar: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    required_bass: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_drum: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_keyboard: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    enrollments = relationship("EventEnrollment", back_populates="event", cascade="all, delete-orphan")


class EventEnrollment(Base):
    __tablename__ = "event_enrollments"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    position: Mapped[BandPosition] = mapped_column(
        Enum(
            BandPosition,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(
            EnrollmentStatus,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=EnrollmentStatus.JOINED,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    event = relationship("Event", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")
