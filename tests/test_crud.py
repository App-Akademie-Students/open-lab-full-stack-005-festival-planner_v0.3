"""Tests for app/crud.py functions not already covered via tests/test_api.py.

acts_for_artists() is the part of the semantic search (B8) that runs on plain joins, so it works
under SQLite; search_top_artists() needs pgvector's cosine_distance() (PostgreSQL only) and is
therefore verified manually against Neon instead (see app/crud.py, roadmap step 9).
"""
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
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


def build_artist(name: str) -> Artist:
    return Artist(name=name, genre="Testgenre", description="Testbeschreibung.")


def build_act(artist: Artist, stage: Stage, starts_at: datetime, ends_at: datetime) -> Act:
    return Act(artist=artist, stage=stage, starts_at=starts_at, ends_at=ends_at)


def test_acts_for_artists_returns_empty_list_for_empty_input(db):
    assert crud.acts_for_artists(db, []) == []


def test_acts_for_artists_orders_by_given_artist_rank(db):
    stage = Stage(name="Hauptbühne")
    ambient = build_artist("Ambient Drift")
    rock = build_artist("Rock Rebels")
    db.add_all(
        [
            build_act(rock, stage, datetime(2026, 9, 18, 13, 0), datetime(2026, 9, 18, 14, 0)),
            build_act(ambient, stage, datetime(2026, 9, 18, 15, 0), datetime(2026, 9, 18, 16, 0)),
        ]
    )
    db.commit()

    # ambient ranked first even though its act starts later - the artist rank wins.
    rows = crud.acts_for_artists(db, [ambient.id, rock.id])

    assert [row.title for row in rows] == ["Ambient Drift", "Rock Rebels"]


def test_acts_for_artists_sorts_chronologically_within_one_artist(db):
    stage = Stage(name="Hauptbühne")
    artist = build_artist("Ambient Drift")
    db.add_all(
        [
            build_act(artist, stage, datetime(2026, 9, 19, 15, 0), datetime(2026, 9, 19, 16, 0)),
            build_act(artist, stage, datetime(2026, 9, 18, 13, 0), datetime(2026, 9, 18, 14, 0)),
        ]
    )
    db.commit()

    rows = crud.acts_for_artists(db, [artist.id])

    assert [row.starts_at for row in rows] == [
        datetime(2026, 9, 18, 13, 0),
        datetime(2026, 9, 19, 15, 0),
    ]


def test_acts_for_artists_excludes_other_artists(db):
    stage = Stage(name="Hauptbühne")
    wanted = build_artist("Ambient Drift")
    other = build_artist("Rock Rebels")
    db.add_all(
        [
            build_act(wanted, stage, datetime(2026, 9, 18, 13, 0), datetime(2026, 9, 18, 14, 0)),
            build_act(other, stage, datetime(2026, 9, 18, 15, 0), datetime(2026, 9, 18, 16, 0)),
        ]
    )
    db.commit()

    rows = crud.acts_for_artists(db, [wanted.id])

    assert [row.title for row in rows] == ["Ambient Drift"]


def test_acts_for_artists_includes_acts_already_ended(db):
    # Unlike list_program(), the search result has no "now"/day filter to leave past acts out.
    stage = Stage(name="Hauptbühne")
    artist = build_artist("Ambient Drift")
    db.add(build_act(artist, stage, datetime(2020, 1, 1, 13, 0), datetime(2020, 1, 1, 14, 0)))
    db.commit()

    rows = crud.acts_for_artists(db, [artist.id])

    assert [row.title for row in rows] == ["Ambient Drift"]


def test_acts_for_artists_includes_genre_and_description(db):
    # Needed for the generated answer's context (B10, app/llm.py).
    stage = Stage(name="Zeltbühne")
    artist = Artist(name="Ambient Drift", genre="Ambient", description="Schwebende Klangflächen.")
    db.add(build_act(artist, stage, datetime(2026, 9, 18, 13, 0), datetime(2026, 9, 18, 14, 0)))
    db.commit()

    [row] = crud.acts_for_artists(db, [artist.id])

    assert (row.genre, row.description) == ("Ambient", "Schwebende Klangflächen.")
