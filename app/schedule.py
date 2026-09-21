"""Business logic: festival time, festival days and 'now' / 'next' status.

Pure functions only - no database, no HTTP - so they are testable without
FastAPI or a database session.
"""
from datetime import date, datetime, time, timedelta, timezone

# Fixed offset UTC+02:00, no DST logic (see CLAUDE.md).
FESTIVAL_TZ = timezone(timedelta(hours=2))


def festival_now() -> datetime:
    """Current festival-local time, naive (no tzinfo attached)."""
    return datetime.now(FESTIVAL_TZ).replace(tzinfo=None)


def festival_day(starts_at: datetime) -> date:
    """The festival day an act belongs to: the day it starts on.

    An act running past midnight (e.g. 23:00-01:00) still belongs to its start day.
    """
    return starts_at.date()


def day_bounds(day: date) -> tuple[datetime, datetime]:
    """Start (inclusive) and end (exclusive) of `day`, for filtering acts by start time."""
    start = datetime.combine(day, time.min)
    return start, start + timedelta(days=1)


def compute_statuses(items, now: datetime) -> list[str | None]:
    """Assign 'now', 'next' or None to each item, aligned with `items` order.

    - 'now': starts_at <= now < ends_at (multiple items possible).
    - 'next': items whose starts_at is the earliest start after `now`
      (multiple items possible on ties).
    - otherwise None.
    """
    upcoming_starts = [item.starts_at for item in items if item.starts_at > now]
    next_start = min(upcoming_starts) if upcoming_starts else None

    statuses: list[str | None] = []
    for item in items:
        if item.starts_at <= now < item.ends_at:
            statuses.append("now")
        elif next_start is not None and item.starts_at == next_start:
            statuses.append("next")
        else:
            statuses.append(None)
    return statuses
