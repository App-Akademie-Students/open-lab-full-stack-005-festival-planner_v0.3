"""Seed script: creates the schema and fills a four-day program starting today.

Run with `python -m app.seed`. Re-running replaces all existing data
(no duplicates).

The tables are dropped and recreated on every run: create_all() only creates missing tables
and never alters existing ones, so this is how schema changes (e.g. new constraints) reach the
database as long as there are no migrations. It also restarts the ID sequences at 1.
"""
from datetime import date, datetime, time, timedelta

from app.db import Base, SessionLocal, engine, init_db
from app.models import Act, Artist, Stage
from app.schedule import festival_now

# (artist name, stage name, start_hour, start_minute, end_hour, end_minute)
# An end time before the start time means the act ends after midnight.
SLOTS_DAY_1 = [
    ("Opener Band", "Hauptbühne", 12, 0, 13, 0),
    ("Folk Trio", "Waldbühne", 12, 0, 13, 0),
    ("DJ Sunrise", "Zeltbühne", 12, 30, 13, 30),
    ("Rock Rebels", "Hauptbühne", 13, 0, 14, 30),
    ("Acoustic Set", "Waldbühne", 13, 30, 14, 30),
    ("Beat Collective", "Zeltbühne", 14, 0, 15, 0),
    ("Indie Waves", "Hauptbühne", 14, 30, 16, 0),
    ("String Quartet", "Waldbühne", 15, 0, 16, 0),
    ("Electro Pulse", "Zeltbühne", 15, 30, 17, 0),
    ("Headliner One", "Hauptbühne", 16, 30, 18, 30),
    ("Chill Session", "Waldbühne", 16, 30, 17, 30),
    ("Bass Drop", "Zeltbühne", 17, 30, 19, 0),
    ("Sunset Groove", "Waldbühne", 18, 0, 19, 0),
    ("Headliner Two", "Hauptbühne", 19, 0, 21, 0),
]

SLOTS_DAY_2 = [
    ("Morning Brass", "Hauptbühne", 12, 0, 13, 0),
    ("Poetry Beats", "Waldbühne", 12, 30, 13, 30),
    ("Techno Garden", "Zeltbühne", 13, 0, 14, 30),
    ("Garage Kings", "Hauptbühne", 14, 0, 15, 30),
    ("Harp & Voice", "Waldbühne", 14, 30, 15, 30),
    ("Dub Station", "Zeltbühne", 15, 0, 16, 30),
    ("Stadium Heroes", "Hauptbühne", 17, 0, 19, 0),
    ("Campfire Songs", "Waldbühne", 17, 30, 19, 0),
    ("Closing Act", "Hauptbühne", 20, 0, 22, 0),
    ("Night Owls", "Zeltbühne", 23, 0, 1, 0),
]

SLOTS_DAY_3 = [
    ("Sunday Swing", "Hauptbühne", 11, 0, 12, 0),
    ("Kids Choir", "Waldbühne", 11, 30, 12, 30),
    ("Ambient Drift", "Zeltbühne", 12, 0, 13, 30),
    ("Punk Parade", "Hauptbühne", 13, 0, 14, 30),
    ("Singer Songwriter", "Waldbühne", 13, 30, 14, 30),
    ("House Nation", "Zeltbühne", 14, 30, 16, 0),
    ("Brass Explosion", "Hauptbühne", 15, 30, 17, 0),
    ("Jazz Corner", "Waldbühne", 16, 0, 17, 30),
    ("Reggae Vibes", "Zeltbühne", 17, 0, 18, 30),
    ("Main Event", "Hauptbühne", 19, 0, 21, 30),
    ("Moonlight Session", "Waldbühne", 20, 0, 21, 0),
    ("Afterhour Collective", "Zeltbühne", 22, 30, 2, 0),
]

SLOTS_DAY_4 = [
    ("Wake Up Yoga Beats", "Waldbühne", 10, 0, 11, 0),
    ("Blues Brothers Tribute", "Hauptbühne", 11, 0, 12, 30),
    ("Lo-Fi Lounge", "Zeltbühne", 11, 30, 13, 0),
    ("Folk Revival", "Waldbühne", 12, 0, 13, 0),
    ("Garage Revival", "Hauptbühne", 13, 0, 14, 30),
    ("Drum Circle", "Zeltbühne", 13, 30, 14, 30),
    ("Farewell Choir", "Waldbühne", 14, 0, 15, 0),
    ("Grand Finale", "Hauptbühne", 15, 0, 17, 0),
]

# One entry per festival day, starting with the seed day.
FESTIVAL_DAYS = [SLOTS_DAY_1, SLOTS_DAY_2, SLOTS_DAY_3, SLOTS_DAY_4]


def build_acts(first_day: date) -> list[Act]:
    # One Stage row per distinct stage name, shared by all its acts (unique constraint).
    stage_names = dict.fromkeys(
        stage_name for slots in FESTIVAL_DAYS for _, stage_name, *_ in slots
    )
    stages = {name: Stage(name=name) for name in stage_names}

    acts = []
    for offset, slots in enumerate(FESTIVAL_DAYS):
        day = first_day + timedelta(days=offset)
        for artist_name, stage_name, sh, sm, eh, em in slots:
            starts_at = datetime.combine(day, time(sh, sm))
            ends_at = datetime.combine(day, time(eh, em))
            if ends_at <= starts_at:
                ends_at += timedelta(days=1)
            acts.append(
                Act(
                    artist=Artist(name=artist_name),
                    stage=stages[stage_name],
                    starts_at=starts_at,
                    ends_at=ends_at,
                )
            )
    return acts


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    init_db()
    acts = build_acts(festival_now().date())

    db = SessionLocal()
    try:
        db.add_all(acts)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
