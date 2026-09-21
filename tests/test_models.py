"""Model tests: database-level invariants (see doc/domain-model.md).

Runs against in-memory SQLite like the API tests - SQLite enforces CHECK
constraints too, so the invariants are covered without touching PostgreSQL.
"""
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Act, Artist, Stage


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def build_act(starts_at: datetime, ends_at: datetime) -> Act:
    return Act(
        artist=Artist(name="Rock Rebels"),
        stage=Stage(name="Hauptbühne"),
        starts_at=starts_at,
        ends_at=ends_at,
    )


def test_act_accepts_end_after_start(db):
    db.add(build_act(datetime(2026, 9, 18, 13, 0), datetime(2026, 9, 18, 14, 0)))
    db.commit()

    assert db.query(Act).count() == 1


def test_act_rejects_end_before_start(db):
    db.add(build_act(datetime(2026, 9, 18, 14, 0), datetime(2026, 9, 18, 13, 0)))

    with pytest.raises(IntegrityError):
        db.commit()


def test_act_rejects_end_equal_to_start(db):
    same = datetime(2026, 9, 18, 13, 0)
    db.add(build_act(same, same))

    with pytest.raises(IntegrityError):
        db.commit()


@pytest.mark.parametrize("name", ["", "   "])
def test_artist_rejects_empty_name(db, name):
    db.add(Artist(name=name))

    with pytest.raises(IntegrityError):
        db.commit()


@pytest.mark.parametrize("name", ["", "   "])
def test_stage_rejects_empty_name(db, name):
    db.add(Stage(name=name))

    with pytest.raises(IntegrityError):
        db.commit()
