from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import EnrollmentStatus
from app.models.event import EventEnrollment
from app.models.practice import PracticeRecord
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, int]:
    total_minutes = db.scalar(
        select(func.coalesce(func.sum(PracticeRecord.duration_minutes), 0)).where(
            PracticeRecord.user_id == current_user.id
        )
    )
    total_practices = db.scalar(
        select(func.count(PracticeRecord.id)).where(PracticeRecord.user_id == current_user.id)
    )
    joined_events = db.scalar(
        select(func.count(EventEnrollment.id)).where(
            EventEnrollment.user_id == current_user.id,
            EventEnrollment.status == EnrollmentStatus.JOINED,
        )
    )
    return {
        "total_minutes": int(total_minutes or 0),
        "total_practices": int(total_practices or 0),
        "joined_events": int(joined_events or 0),
    }
