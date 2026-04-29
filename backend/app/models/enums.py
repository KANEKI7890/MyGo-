from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


class BandPosition(StrEnum):
    VOCAL = "vocal"
    GUITAR = "guitar"
    BASS = "bass"
    DRUM = "drum"
    KEYBOARD = "keyboard"


class InstrumentType(StrEnum):
    VOCAL = "vocal"
    GUITAR = "guitar"
    BASS = "bass"
    DRUM = "drum"
    KEYBOARD = "keyboard"


class EventStatus(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    FULL = "full"
    COMPLETED = "completed"
    CANCELED = "canceled"


class EnrollmentStatus(StrEnum):
    JOINED = "joined"
    CANCELED = "canceled"
