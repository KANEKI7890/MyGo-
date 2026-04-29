from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import BandPosition, UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    band_position: BandPosition
    bio: str | None = Field(default=None, max_length=500)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=80)
    band_position: BandPosition | None = None
    bio: str | None = Field(default=None, max_length=500)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole
    band_position: BandPosition
    bio: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
