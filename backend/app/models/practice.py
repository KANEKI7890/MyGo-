from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InstrumentType


class PracticeRecord(Base):
    __tablename__ = "practice_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    instrument: Mapped[InstrumentType] = mapped_column(
        Enum(
            InstrumentType,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    practiced_on: Mapped[date] = mapped_column(Date, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    song_title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="practices")
