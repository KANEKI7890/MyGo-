from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.api.routes.events import serialize_event
from app.db.session import get_db
from app.models.enums import EnrollmentStatus
from app.models.event import Event, EventEnrollment
from app.models.user import User
from app.schemas.event import EventRead

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/me", response_model=list[EventRead])
def my_schedule(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[EventRead]:
    stmt = (
        select(Event)
        .join(EventEnrollment)
        .options(selectinload(Event.enrollments).selectinload(EventEnrollment.user))
        .where(
            EventEnrollment.user_id == current_user.id,
            EventEnrollment.status == EnrollmentStatus.JOINED,
        )
        .order_by(Event.starts_at.asc())
    )
    return [serialize_event(event, current_user) for event in db.scalars(stmt).all()]
