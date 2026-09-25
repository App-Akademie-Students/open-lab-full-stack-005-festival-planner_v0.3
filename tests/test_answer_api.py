"""Tests for GET /api/answer (generated answer, C12/B10, roadmap phase 2 step 9).

Like tests/test_search_api.py, `search_artist_ids` is overridden (no embedding model, no
pgvector under SQLite) and `festival_now` is fixed. `llm_send` is replaced by a fake, so no
running Ollama is needed; what the fake receives shows which context reached the LLM.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.llm import LLMUnavailableError
from app.main import app
from app.models import Act, Artist, Stage
from app.routers import llm_send, search_artist_ids
from app.schedule import festival_now

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

NOW = datetime(2026, 9, 18, 14, 0)

client = TestClient(app)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[festival_now] = lambda: NOW
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def artist_ids_override():
    """Sets which artist ids search_artist_ids() returns; empty by default (no hits)."""
    ids: list[int] = []
    app.dependency_overrides[search_artist_ids] = lambda: ids
    return ids


@pytest.fixture
def llm_requests():
    """Replaces the Ollama call; records every request body and answers with a fixed text."""
    requests: list[dict] = []

    def send(body):
        requests.append(body)
        return {"message": {"role": "assistant", "content": " Brass Explosion spielt um 15 Uhr. "}}

    app.dependency_overrides[llm_send] = lambda: send
    return requests


def add_brass_explosion() -> int:
    """One artist with one act at 15:00-16:00 on the NOW day; returns the artist id."""
    db = TestSessionLocal()
    artist = Artist(name="Brass Explosion", genre="Brass, Funk", description="Brassband mit Funk.")
    db.add(
        Act(
            artist=artist,
            stage=Stage(name="Hauptbühne"),
            starts_at=datetime(2026, 9, 18, 15, 0),
            ends_at=datetime(2026, 9, 18, 16, 0),
        )
    )
    db.commit()
    artist_id = artist.id
    db.close()
    return artist_id


def test_answer_requires_a_query_param():
    assert client.get("/api/answer").status_code == 422


def test_answer_rejects_whitespace_only_query():
    assert client.get("/api/answer", params={"q": "   "}).status_code == 422


def test_answer_without_hits_does_not_call_the_llm(artist_ids_override, llm_requests):
    response = client.get("/api/answer", params={"q": "Heavy Metal"})

    assert response.status_code == 200
    assert response.json() == {"status": "no_hits", "answer": None}
    assert llm_requests == []


def test_answer_returns_generated_text_based_on_the_hits(artist_ids_override, llm_requests):
    artist_ids_override.append(add_brass_explosion())

    response = client.get("/api/answer", params={"q": "  Wo gibt es Blasmusik?  "})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "answer": "Brass Explosion spielt um 15 Uhr."}
    [request] = llm_requests
    user_message = request["messages"][1]["content"]
    assert "Artist: Brass Explosion" in user_message
    assert "Status: kommt noch" in user_message  # computed from the fixed NOW (14:00)
    assert user_message.endswith("Frage: Wo gibt es Blasmusik?")  # trimmed question


def test_answer_reports_unavailable_llm(artist_ids_override):
    artist_ids_override.append(add_brass_explosion())

    def failing_send(body):
        raise LLMUnavailableError("Ollama request failed: connection refused")

    app.dependency_overrides[llm_send] = lambda: failing_send

    response = client.get("/api/answer", params={"q": "Wo gibt es Blasmusik?"})

    assert response.status_code == 200
    assert response.json() == {"status": "unavailable", "answer": None}


def test_answer_with_facts_not_in_the_hits_is_dropped(artist_ids_override):
    # Grounding check (step 11): the act plays at 15:00, the "answer" invents 20:00.
    artist_ids_override.append(add_brass_explosion())

    def inventing_send(body):
        return {"message": {"content": "Brass Explosion spielt um 20:00 auf der Hauptbühne."}}

    app.dependency_overrides[llm_send] = lambda: inventing_send

    response = client.get("/api/answer", params={"q": "Wo gibt es Blasmusik?"})

    assert response.json() == {"status": "unavailable", "answer": None}


def test_search_is_unchanged_by_the_answer_endpoint(artist_ids_override):
    # /api/search must not call the LLM and keeps its response shape (no answer field).
    artist_ids_override.append(add_brass_explosion())

    body = client.get("/api/search", params={"q": "Blasmusik"}).json()

    assert list(body) == ["items"]
    assert [item["title"] for item in body["items"]] == ["Brass Explosion"]
