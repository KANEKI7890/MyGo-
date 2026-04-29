from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.practice import PracticeRecord
from app.models.user import User
from app.schemas.practice import PracticeCreate, PracticeRead, PracticeSummary, PracticeUpdate

router = APIRouter(prefix="/practices", tags=["practices"])


@router.get("", response_model=list[PracticeRead])
def list_practices(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[PracticeRecord]:
    stmt = (
        select(PracticeRecord)
        .where(PracticeRecord.user_id == current_user.id)
        .order_by(desc(PracticeRecord.practiced_on), desc(PracticeRecord.created_at))
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=PracticeRead, status_code=status.HTTP_201_CREATED)
def create_practice(
    payload: PracticeCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PracticeRecord:
    record = PracticeRecord(user_id=current_user.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{practice_id}", response_model=PracticeRead)
def update_practice(
    practice_id: int,
    payload: PracticeUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PracticeRecord:
    record = db.scalar(
        select(PracticeRecord).where(
            PracticeRecord.id == practice_id, PracticeRecord.user_id == current_user.id
        )
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice record not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{practice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_practice(
    practice_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    record = db.scalar(
        select(PracticeRecord).where(
            PracticeRecord.id == practice_id, PracticeRecord.user_id == current_user.id
        )
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice record not found")
    db.delete(record)
    db.commit()


@router.get("/summary", response_model=PracticeSummary)
def practice_summary(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PracticeSummary:
    records = db.scalars(select(PracticeRecord).where(PracticeRecord.user_id == current_user.id)).all()
    by_instrument: dict[str, int] = {}
    for record in records:
        by_instrument[record.instrument.value] = (
            by_instrument.get(record.instrument.value, 0) + record.duration_minutes
        )
    return PracticeSummary(
        total_sessions=len(records),
        total_minutes=sum(record.duration_minutes for record in records),
        by_instrument=by_instrument,
    )
