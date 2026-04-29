from app.models.enums import BandPosition, EnrollmentStatus, EventStatus
from app.models.event import Event
from app.schemas.event import PositionDemand


POSITION_TO_FIELD = {
    BandPosition.VOCAL: "vocal",
    BandPosition.GUITAR: "guitar",
    BandPosition.BASS: "bass",
    BandPosition.DRUM: "drum",
    BandPosition.KEYBOARD: "keyboard",
}


def requirements_from_event(event: Event) -> PositionDemand:
    return PositionDemand(
        vocal=event.required_vocal,
        guitar=event.required_guitar,
        bass=event.required_bass,
        drum=event.required_drum,
        keyboard=event.required_keyboard,
    )


def apply_requirements(event: Event, requirements: PositionDemand) -> None:
    event.required_vocal = requirements.vocal
    event.required_guitar = requirements.guitar
    event.required_bass = requirements.bass
    event.required_drum = requirements.drum
    event.required_keyboard = requirements.keyboard


def filled_from_event(event: Event) -> PositionDemand:
    filled = PositionDemand(vocal=0, guitar=0, bass=0, drum=0, keyboard=0)
    for enrollment in event.enrollments:
        if enrollment.status != EnrollmentStatus.JOINED:
            continue
        field = POSITION_TO_FIELD[enrollment.position]
        setattr(filled, field, getattr(filled, field) + 1)
    return filled


def available_slots(event: Event) -> PositionDemand:
    required = requirements_from_event(event)
    filled = filled_from_event(event)
    return PositionDemand(
        vocal=max(required.vocal - filled.vocal, 0),
        guitar=max(required.guitar - filled.guitar, 0),
        bass=max(required.bass - filled.bass, 0),
        drum=max(required.drum - filled.drum, 0),
        keyboard=max(required.keyboard - filled.keyboard, 0),
    )


def required_for_position(event: Event, position: BandPosition) -> int:
    field = POSITION_TO_FIELD[position]
    return getattr(requirements_from_event(event), field)


def filled_for_position(event: Event, position: BandPosition) -> int:
    field = POSITION_TO_FIELD[position]
    return getattr(filled_from_event(event), field)


def has_capacity_for(event: Event, position: BandPosition) -> bool:
    return required_for_position(event, position) > filled_for_position(event, position)


def mark_full_if_needed(event: Event) -> None:
    if event.status not in {EventStatus.OPEN, EventStatus.FULL}:
        return
    available = available_slots(event)
    event.status = (
        EventStatus.FULL
        if all(value == 0 for value in available.model_dump().values())
        else EventStatus.OPEN
    )
