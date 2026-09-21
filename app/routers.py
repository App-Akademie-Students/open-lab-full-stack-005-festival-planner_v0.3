"""API endpoints: GET /api/program, GET /api/stages, GET /api/days."""
from datetime import date, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud
from app.db import get_db
from app.schedule import compute_statuses, festival_now

router = APIRouter()


class ProgramItemOut(BaseModel):
    id: int
    title: str
    stage: str
    starts_at: datetime
    ends_at: datetime
    status: str | None


class ProgramResponse(BaseModel):
    now: datetime
    items: list[ProgramItemOut]


@router.get("/api/stages")
def get_stages(db: Session = Depends(get_db)) -> list[str]:
    return crud.list_stages(db)


@router.get("/api/days")
def get_days(db: Session = Depends(get_db)) -> list[date]:
    return crud.list_days(db)


@router.get("/api/program", response_model=ProgramResponse)
def get_program(
    stage: str | None = None,
    day: date | None = None,
    db: Session = Depends(get_db),
    now: datetime = Depends(festival_now),
) -> ProgramResponse:
    rows = crud.list_program(db, stage=stage, day=day)
    statuses = compute_statuses(rows, now)
    items = [
        ProgramItemOut(
            id=row.id,
            title=row.title,
            stage=row.stage,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
            status=status,
        )
        for row, status in zip(rows, statuses)
    ]
    return ProgramResponse(now=now, items=items)
