"""Unit tests for app.schedule - pure functions, no DB, no HTTP."""
from dataclasses import dataclass
from datetime import date, datetime

from app.schedule import compute_statuses, day_bounds, festival_day


@dataclass
class Item:
    title: str
    starts_at: datetime
    ends_at: datetime


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 9, 11, hour, minute)


def test_exactly_at_start_is_now():
    item = Item("A", dt(12, 0), dt(13, 0))
    assert compute_statuses([item], dt(12, 0)) == ["now"]


def test_exactly_at_end_is_not_now():
    item = Item("A", dt(12, 0), dt(13, 0))
    assert compute_statuses([item], dt(13, 0)) == [None]


def test_multiple_items_running_at_once():
    a = Item("A", dt(12, 0), dt(13, 0))
    b = Item("B", dt(12, 0), dt(14, 0))
    assert compute_statuses([a, b], dt(12, 30)) == ["now", "now"]


def test_earliest_upcoming_item_is_next():
    a = Item("A", dt(12, 0), dt(13, 0))
    b = Item("B", dt(14, 0), dt(15, 0))
    assert compute_statuses([a, b], dt(13, 30)) == [None, "next"]


def test_multiple_items_with_same_next_start_time():
    a = Item("A", dt(14, 0), dt(15, 0))
    b = Item("B", dt(14, 0), dt(15, 30))
    c = Item("C", dt(16, 0), dt(17, 0))
    assert compute_statuses([a, b, c], dt(13, 0)) == ["next", "next", None]


def test_before_festival_start_only_next_no_now():
    a = Item("A", dt(12, 0), dt(13, 0))
    b = Item("B", dt(12, 0), dt(14, 0))
    assert compute_statuses([a, b], dt(10, 0)) == ["next", "next"]


def test_after_last_item_nothing_highlighted():
    a = Item("A", dt(12, 0), dt(13, 0))
    b = Item("B", dt(13, 0), dt(14, 0))
    assert compute_statuses([a, b], dt(15, 0)) == [None, None]


def test_next_is_computed_within_given_items_only():
    # Simulates a stage-filtered list: only items on one stage are passed in,
    # so "next" must be relative to that subset, not the full program.
    filtered = [Item("C", dt(16, 0), dt(17, 0))]
    assert compute_statuses(filtered, dt(13, 0)) == ["next"]


def test_act_belongs_to_its_start_day():
    assert festival_day(datetime(2026, 9, 11, 12, 0)) == date(2026, 9, 11)


def test_act_past_midnight_belongs_to_its_start_day():
    # 23:00-01:00: the act starts on the 11th, so it belongs to the 11th.
    assert festival_day(datetime(2026, 9, 11, 23, 0)) == date(2026, 9, 11)


def test_day_bounds_cover_exactly_one_day():
    start, end = day_bounds(date(2026, 9, 11))
    assert start == datetime(2026, 9, 11, 0, 0)
    assert end == datetime(2026, 9, 12, 0, 0)
