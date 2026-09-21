"""Tests for the seed data built by app.seed.build_acts - pure, no DB needed.

The seed data is what US-8 (day grouping and filter) is checked against in the browser,
so its day and midnight logic is tested here.
"""
from datetime import date, datetime

from app.schedule import festival_day
from app.seed import FESTIVAL_DAYS, build_acts

FIRST_DAY = date(2026, 9, 18)


def acts_by_artist():
    return {act.artist.name: act for act in build_acts(FIRST_DAY)}


def test_one_act_per_slot():
    assert len(build_acts(FIRST_DAY)) == sum(len(slots) for slots in FESTIVAL_DAYS)


def test_acts_span_consecutive_days_from_first_day():
    days = sorted({festival_day(act.starts_at) for act in build_acts(FIRST_DAY)})
    assert days == [date(2026, 9, 18), date(2026, 9, 19), date(2026, 9, 20), date(2026, 9, 21)]


def test_every_act_ends_after_it_starts():
    assert all(act.ends_at > act.starts_at for act in build_acts(FIRST_DAY))


def test_act_past_midnight_ends_on_the_next_day():
    # Slot "23:00-01:00" on day 2: the end time lies before the start time on the clock.
    night_owls = acts_by_artist()["Night Owls"]
    assert night_owls.starts_at == datetime(2026, 9, 19, 23, 0)
    assert night_owls.ends_at == datetime(2026, 9, 20, 1, 0)
    assert festival_day(night_owls.starts_at) == date(2026, 9, 19)


def test_stages_are_shared_between_acts():
    # One Stage object per name, otherwise the unique constraint on Stage.name would fail.
    acts = build_acts(FIRST_DAY)
    assert len({id(act.stage) for act in acts}) == len({act.stage.name for act in acts})
