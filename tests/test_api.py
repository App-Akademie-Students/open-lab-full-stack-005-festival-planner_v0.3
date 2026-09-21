"""API tests: sorting, stage and day filter, stage and day list, status field."""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Act, Artist, Stage
from app.schedule import festival_now

# In-memory SQLite only exists per connection - StaticPool makes every
# session share the same connection, so all sessions see the same data.
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


def override_festival_now():
    return datetime(2026, 9, 11, 14, 0)


client = TestClient(app)


# Overrides are set per test and removed afterwards, so they cannot leak into other test
# modules that use the same app object.
@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[festival_now] = override_festival_now
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    hauptbuehne = Stage(name="Hauptbühne")
    waldbuehne = Stage(name="Waldbühne")
    zeltbuehne = Stage(name="Zeltbühne")

    db = TestSessionLocal()
    db.add_all(
        [
            Act(
                artist=Artist(name="Rock Rebels"),
                stage=hauptbuehne,
                starts_at=datetime(2026, 9, 11, 13, 0),
                ends_at=datetime(2026, 9, 11, 14, 30),
            ),
            Act(
                artist=Artist(name="Folk Trio"),
                stage=waldbuehne,
                starts_at=datetime(2026, 9, 11, 12, 0),
                ends_at=datetime(2026, 9, 11, 13, 0),
            ),
            Act(
                artist=Artist(name="DJ Sunrise"),
                stage=zeltbuehne,
                starts_at=datetime(2026, 9, 11, 12, 0),
                ends_at=datetime(2026, 9, 11, 13, 0),
            ),
            Act(
                artist=Artist(name="Headliner"),
                stage=hauptbuehne,
                starts_at=datetime(2026, 9, 11, 16, 0),
                ends_at=datetime(2026, 9, 11, 18, 0),
            ),
        ]
    )
    db.commit()
    db.close()
    yield


def test_program_is_sorted_by_start_then_stage():
    response = client.get("/api/program")
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Folk Trio", "DJ Sunrise", "Rock Rebels", "Headliner"]


def test_program_includes_status_and_now():
    response = client.get("/api/program")
    body = response.json()
    assert body["now"] == "2026-09-11T14:00:00"
    statuses = {item["title"]: item["status"] for item in body["items"]}
    assert statuses["Rock Rebels"] == "now"
    assert statuses["Headliner"] == "next"
    assert statuses["Folk Trio"] is None
    assert statuses["DJ Sunrise"] is None


def test_program_filtered_by_stage():
    response = client.get("/api/program", params={"stage": "Hauptbühne"})
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Rock Rebels", "Headliner"]


def test_program_filtered_by_unknown_stage_returns_empty_list():
    response = client.get("/api/program", params={"stage": "Nirgendwo"})
    assert response.json()["items"] == []


def test_stages_are_sorted_alphabetically():
    response = client.get("/api/stages")
    assert response.json() == ["Hauptbühne", "Waldbühne", "Zeltbühne"]


def test_root_serves_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def add_second_day():
    """Adds acts on 2026-09-12, one of them running past midnight into the 13th."""
    db = TestSessionLocal()
    hauptbuehne = db.query(Stage).filter_by(name="Hauptbühne").one()
    zeltbuehne = db.query(Stage).filter_by(name="Zeltbühne").one()
    db.add_all(
        [
            Act(
                artist=Artist(name="Morning Brass"),
                stage=hauptbuehne,
                starts_at=datetime(2026, 9, 12, 12, 0),
                ends_at=datetime(2026, 9, 12, 13, 0),
            ),
            Act(
                artist=Artist(name="Night Owls"),
                stage=zeltbuehne,
                starts_at=datetime(2026, 9, 12, 23, 0),
                ends_at=datetime(2026, 9, 13, 1, 0),
            ),
        ]
    )
    db.commit()
    db.close()


def test_days_are_sorted_and_use_the_start_day():
    add_second_day()
    response = client.get("/api/days")
    # No 2026-09-13: "Night Owls" ends then, but starts on the 12th.
    assert response.json() == ["2026-09-11", "2026-09-12"]


def test_program_filtered_by_day():
    add_second_day()
    response = client.get("/api/program", params={"day": "2026-09-12"})
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Morning Brass", "Night Owls"]


def test_program_filtered_by_day_and_stage():
    add_second_day()
    response = client.get("/api/program", params={"day": "2026-09-12", "stage": "Zeltbühne"})
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Night Owls"]


def test_program_filtered_by_day_without_acts_returns_empty_list():
    response = client.get("/api/program", params={"day": "2026-09-20"})
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_program_filtered_by_invalid_day_is_rejected():
    response = client.get("/api/program", params={"day": "morgen"})
    assert response.status_code == 422


def test_status_is_computed_within_the_selected_day():
    # now = 2026-09-11 14:00. On the 12th nothing runs yet, so its first act is "next".
    add_second_day()
    response = client.get("/api/program", params={"day": "2026-09-12"})
    statuses = {item["title"]: item["status"] for item in response.json()["items"]}
    assert statuses == {"Morning Brass": "next", "Night Owls": None}


def test_program_and_stages_with_empty_database():
    db = TestSessionLocal()
    db.query(Act).delete()
    db.query(Artist).delete()
    db.query(Stage).delete()
    db.commit()
    db.close()

    program_response = client.get("/api/program")
    assert program_response.status_code == 200
    assert program_response.json()["items"] == []

    stages_response = client.get("/api/stages")
    assert stages_response.status_code == 200
    assert stages_response.json() == []

    days_response = client.get("/api/days")
    assert days_response.status_code == 200
    assert days_response.json() == []
