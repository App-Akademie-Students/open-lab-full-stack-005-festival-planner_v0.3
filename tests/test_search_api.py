"""Tests for GET /api/search (semantic search, B8/F11, roadmap step 11).

`search_artist_ids` is overridden like `festival_now` in tests/test_api.py: it embeds the
query and ranks artists via pgvector, neither of which the SQLite test database supports (see
app/crud.py, roadmap step 10). Overriding it lets these tests exercise the rest of the endpoint
- request validation, joining to acts, and the response shape - without the real model or
PostgreSQL.
"""
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Act, Artist, Stage
from app.routers import search_artist_ids

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_artist(name: str) -> Artist:
    return Artist(name=name, genre="Testgenre", description="Testbeschreibung.")


client = TestClient(app)


@pytest.fixture
def artist_ids_override():
    """Sets which artist ids search_artist_ids() returns; empty by default (no ranking done)."""
    ids: list[int] = []
    app.dependency_overrides[search_artist_ids] = lambda: ids
    yield ids
    app.dependency_overrides.pop(search_artist_ids, None)


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_search_requires_a_query_param():
    response = client.get("/api/search")
    assert response.status_code == 422


def test_search_rejects_empty_query():
    response = client.get("/api/search", params={"q": ""})
    assert response.status_code == 422


def test_search_rejects_whitespace_only_query():
    response = client.get("/api/search", params={"q": "   "})
    assert response.status_code == 422


def test_search_with_no_matching_artists_returns_empty_list(artist_ids_override):
    response = client.get("/api/search", params={"q": "ruhige elektronische Musik"})
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_search_returns_acts_in_artist_rank_order(artist_ids_override):
    stage = Stage(name="Hauptbühne")
    ambient = make_artist("Ambient Drift")
    rock = make_artist("Rock Rebels")
    db = TestSessionLocal()
    db.add_all(
        [
            Act(
                artist=rock,
                stage=stage,
                starts_at=datetime(2026, 9, 18, 13, 0),
                ends_at=datetime(2026, 9, 18, 14, 0),
            ),
            Act(
                artist=ambient,
                stage=stage,
                starts_at=datetime(2026, 9, 18, 15, 0),
                ends_at=datetime(2026, 9, 18, 16, 0),
            ),
        ]
    )
    db.commit()
    db.refresh(ambient)
    db.refresh(rock)
    # ambient ranked first even though its act starts later.
    artist_ids_override.extend([ambient.id, rock.id])
    db.close()

    response = client.get("/api/search", params={"q": "ruhige elektronische Musik"})

    body = response.json()
    assert [item["title"] for item in body["items"]] == ["Ambient Drift", "Rock Rebels"]
    first = body["items"][0]
    assert first["stage"] == "Hauptbühne"
    assert first["day"] == "2026-09-18"
    assert first["starts_at"] == "2026-09-18T15:00:00"
    assert first["ends_at"] == "2026-09-18T16:00:00"
