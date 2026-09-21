"""Database queries: stage list, day list and program list (joins over Artist/Stage).

Program rows come back already flattened to `title`/`stage` - the API
contract stays flat (see architecture.md, T-4), so callers don't need to
know about `Artist`/`Stage` at all.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models import Act, Artist, Stage
from app.schedule import day_bounds, festival_day


def list_stages(db: Session) -> list[str]:
    """Alphabetically sorted stage names, for the filter dropdown."""
    rows = db.query(Stage.name).order_by(Stage.name).all()
    return [row[0] for row in rows]


def list_days(db: Session) -> list[date]:
    """Chronologically sorted festival days that have at least one act, for the day filter."""
    rows = db.query(Act.starts_at).distinct().all()
    return sorted({festival_day(row.starts_at) for row in rows})


def list_program(db: Session, stage: str | None = None, day: date | None = None):
    """Acts chronologically sorted, joined to Artist/Stage, optionally filtered by stage and day.

    The day filter uses the act's start time (see `schedule.festival_day`); it is a
    range filter instead of a date() cast so it works the same on PostgreSQL and SQLite.

    Returns rows with `.id`, `.title`, `.stage`, `.starts_at`, `.ends_at`.
    """
    query = (
        db.query(
            Act.id,
            Artist.name.label("title"),
            Stage.name.label("stage"),
            Act.starts_at,
            Act.ends_at,
        )
        .join(Artist)
        .join(Stage)
        .order_by(Act.starts_at, Stage.name)
    )
    if stage is not None:
        query = query.filter(Stage.name == stage)
    if day is not None:
        day_start, day_end = day_bounds(day)
        query = query.filter(Act.starts_at >= day_start, Act.starts_at < day_end)
    return query.all()
