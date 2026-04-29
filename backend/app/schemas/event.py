from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BandPosition, EnrollmentStatus, EventStatus
from app.schemas.user import UserRead


class PositionDemand(BaseModel):
    vocal: int = Field(default=1, ge=0, le=20)
    guitar: int = Field(default=2, ge=0, le=20)
    bass: int = Field(default=1, ge=0, le=20)
    drum: int = Field(default=1, ge=0, le=20)
    keyboard: int = Field(default=0, ge=0, le=20)


class EventBase(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    venue: str | None = Field(default=None, max_length=160)
    starts_at: datetime
    ends_at: datetime | None = None
    description: str | None = None
    status: EventStatus = EventStatus.OPEN
    requirements: PositionDemand = Field(default_factory=PositionDemand)

    @model_validator(mode="after")
    def validate_time_range(self) -> "EventBase":
        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be later than starts_at")
        return self


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    venue: str | None = Field(default=None, max_length=160)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    description: str | None = None
    status: EventStatus | None = None
    requirements: PositionDemand | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> "EventUpdate":
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be later than starts_at")
        return self


class EventParticipant(BaseModel):
    id: int
    position: BandPosition
    status: EnrollmentStatus
    joined_at: datetime
    user: UserRead

    model_config = ConfigDict(from_attributes=True)


class EventRead(BaseModel):
    id: int
    title: str
    venue: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    description: str | None = None
    status: EventStatus
    requirements: PositionDemand
    filled: PositionDemand
    available: PositionDemand
    participants: list[EventParticipant] = []
    is_joined: bool = False
    can_join: bool = False
    matched_position: BandPosition | None = None
    created_by_id: int | None = None
    created_at: datetime
    updated_at: datetime


class EventJoinResult(BaseModel):
    message: str
    event: EventRead
