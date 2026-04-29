from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.enums import BandPosition, EnrollmentStatus, EventStatus
from app.models.event import Event, EventEnrollment
from app.models.user import User
from app.schemas.event import EventCreate, EventJoinResult, EventParticipant, EventRead, EventUpdate
from app.services.event_matching import (
    apply_requirements,
    available_slots,
    filled_from_event,
    filled_for_position,
    has_capacity_for,
    mark_full_if_needed,
    required_for_position,
    requirements_from_event,
)

router = APIRouter(prefix="/events", tags=["events"])


def event_options():
    return selectinload(Event.enrollments).selectinload(EventEnrollment.user)


def load_event(db: Session, event_id: int) -> Event:
    event = db.scalar(select(Event).options(event_options()).where(Event.id == event_id))
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


def serialize_event(event: Event, current_user: User) -> EventRead:
    joined_enrollments = [
        enrollment for enrollment in event.enrollments if enrollment.status == EnrollmentStatus.JOINED
    ]
    is_joined = any(enrollment.user_id == current_user.id for enrollment in joined_enrollments)
    can_join = (
        event.status == EventStatus.OPEN
        and not is_joined
        and required_for_position(event, current_user.band_position) > 0
        and has_capacity_for(event, current_user.band_position)
    )
    return EventRead(
        id=event.id,
        title=event.title,
        venue=event.venue,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        description=event.description,
        status=event.status,
        requirements=requirements_from_event(event),
        filled=filled_from_event(event),
        available=available_slots(event),
        participants=[EventParticipant.model_validate(enrollment) for enrollment in joined_enrollments],
        is_joined=is_joined,
        can_join=can_join,
        matched_position=current_user.band_position
        if required_for_position(event, current_user.band_position) > 0
        else None,
        created_by_id=event.created_by_id,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.get("", response_model=list[EventRead])
def list_events(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[EventRead]:
    events = db.scalars(select(Event).options(event_options()).order_by(Event.starts_at.asc())).all()
    return [serialize_event(event, current_user) for event in events]


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)],
) -> EventRead:
    event = Event(
        title=payload.title,
        venue=payload.venue,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        description=payload.description,
        status=payload.status,
        created_by_id=admin.id,
    )
    apply_requirements(event, payload.requirements)
    db.add(event)
    db.commit()
    event = load_event(db, event.id)
    mark_full_if_needed(event)
    db.commit()
    return serialize_event(event, admin)


@router.get("/{event_id}", response_model=EventRead)
def read_event(
    event_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventRead:
    return serialize_event(load_event(db, event_id), current_user)


@router.patch("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)],
) -> EventRead:
    event = load_event(db, event_id)
    updates = payload.model_dump(exclude_unset=True)
    requirements = updates.pop("requirements", None)
    for key, value in updates.items():
        setattr(event, key, value)

    if requirements:
        for position, requested in requirements.model_dump().items():
            enum_position = BandPosition(position)
            if requested < filled_for_position(event, enum_position):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot set {position} below current joined count",
                )
        apply_requirements(event, requirements)

    mark_full_if_needed(event)
    db.add(event)
    db.commit()
    event = load_event(db, event.id)
    return serialize_event(event, admin)


@router.post("/{event_id}/join", response_model=EventJoinResult)
def join_event(
    event_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventJoinResult:
    event = load_event(db, event_id)
    if event.status != EventStatus.OPEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is not open for joining")

    position = current_user.band_position
    if required_for_position(event, position) <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This event does not need your position")
    if not has_capacity_for(event, position):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your position is already full")

    existing = next((item for item in event.enrollments if item.user_id == current_user.id), None)
    if existing and existing.status == EnrollmentStatus.JOINED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined this event")

    if existing:
        existing.status = EnrollmentStatus.JOINED
        existing.position = position
        db.add(existing)
    else:
        enrollment = EventEnrollment(event=event, user=current_user, position=position)
        db.add(enrollment)

    mark_full_if_needed(event)
    db.add(event)
    db.commit()
    event = load_event(db, event.id)
    return EventJoinResult(message="Joined event and added to your schedule", event=serialize_event(event, current_user))


@router.post("/{event_id}/leave", response_model=EventJoinResult)
def leave_event(
    event_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventJoinResult:
    event = load_event(db, event_id)
    enrollment = next(
        (
            item
            for item in event.enrollments
            if item.user_id == current_user.id and item.status == EnrollmentStatus.JOINED
        ),
        None,
    )
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have not joined this event")

    enrollment.status = EnrollmentStatus.CANCELED
    db.add(enrollment)
    mark_full_if_needed(event)
    db.add(event)
    db.commit()
    event = load_event(db, event.id)
    return EventJoinResult(message="Removed from your schedule", event=serialize_event(event, current_user))
