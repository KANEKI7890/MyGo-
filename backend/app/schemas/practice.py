from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import InstrumentType


class PracticeCreate(BaseModel):
    instrument: InstrumentType
    practiced_on: date
    duration_minutes: int = Field(gt=0, le=1440)
    song_title: str | None = Field(default=None, max_length=160)
    note: str | None = None


class PracticeUpdate(BaseModel):
    instrument: InstrumentType | None = None
    practiced_on: date | None = None
    duration_minutes: int | None = Field(default=None, gt=0, le=1440)
    song_title: str | None = Field(default=None, max_length=160)
    note: str | None = None


class PracticeRead(BaseModel):
    id: int
    user_id: int
    instrument: InstrumentType
    practiced_on: date
    duration_minutes: int
    song_title: str | None = None
    note: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PracticeSummary(BaseModel):
    total_sessions: int
    total_minutes: int
    by_instrument: dict[str, int]
