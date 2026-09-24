"""Database queries: stage list, day list, program list (joins over Artist/Stage), artist list.

Program rows come back already flattened to `title`/`stage` - the API
contract stays flat (see architecture.md, T-4), so callers don't need to
know about `Artist`/`Stage` at all.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models import Act, Artist, Stage
from app.schedule import day_bounds, festival_day

# Semantic search (B8): fixed number of matching artists, no minimum-similarity cutoff - the
# closest artists are always returned, even for a query with no good match. Chosen over a
# distance threshold because a good cutoff value has no principled default and would need
# separate tuning per embedding model.
SEARCH_ARTIST_LIMIT = 5


def list_stages(db: Session) -> list[str]:
    """Alphabetically sorted stage names, for the filter dropdown."""
    rows = db.query(Stage.name).order_by(Stage.name).all()
    return [row[0] for row in rows]


def list_days(db: Session) -> list[date]: # TODO learning
    """Chronologically sorted festival days that have at least one act, for the day filter."""
    rows = db.query(Act.starts_at).distinct().all()
    return sorted({festival_day(row.starts_at) for row in rows})


def list_program(db: Session, stage: str | None = None, day: date | None = None):
    """Acts chronologically sorted, joined to Artist/Stage, optionally filtered by stage and day.

    The day filter uses the act's start time (see `schedule.festival_day`); it is a
    range filter instead of a date() cast so it works the same on PostgreSQL and SQLite.

    Returns rows with `.id`, `.title`, `.stage`, `.starts_at`, `.ends_at`.
    """
    # SELECT act.id, artist.name AS title, stage.name AS stage,
    #        act.starts_at, act.ends_at
    # FROM act
    # JOIN artist ON artist.id = act.artist_id
    # JOIN stage ON stage.id = act.stage_id
    # ORDER BY act.starts_at, stage.name
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


def list_artists(db: Session) -> list[Artist]:
    """All artists as ORM objects sorted by id, e.g. to (re)generate their embeddings."""
    return db.query(Artist).order_by(Artist.id).all()


def search_top_artists(
    db: Session, query_vector: list[float], limit: int = SEARCH_ARTIST_LIMIT
) -> list[int]:
    """Ids of the `limit` artists whose embedding is closest to `query_vector`, closest first.

    Uses pgvector's cosine distance operator (`<=>`) via `Column.cosine_distance()`; both
    `query_vector` and the stored embeddings are normalized to length 1 (see
    `app/embeddings.py`), so this ranks the same as inner product would. Artists without an
    embedding (not yet generated, see roadmap step 8) are excluded.

    Requires PostgreSQL with pgvector - SQLite (used in tests) has no `cosine_distance`, so this
    function is verified manually against Neon (roadmap step 9) rather than by an automated
    test; `acts_for_artists()` below covers the rest of the search with tests.
    """
    # SELECT artist.id
    # FROM artist
    # WHERE artist.embedding IS NOT NULL
    # ORDER BY artist.embedding <=> :query_vector
    # LIMIT :limit
    rows = (
        db.query(Artist.id)
        .filter(Artist.embedding.is_not(None))
        .order_by(Artist.embedding.cosine_distance(query_vector))
        .limit(limit)
        .all()
    )
    return [artist_id for (artist_id,) in rows]


def acts_for_artists(db: Session, artist_ids: list[int]):
    """Acts of the given artists, ordered like `artist_ids` and chronologically within an artist.

    Same flat row shape as `list_program()`: `.id`, `.title`, `.stage`, `.starts_at`, `.ends_at`.
    Used for the search result (B8): every act of a matching artist is a hit, independent of any
    day/stage filter, including acts that have already ended - unlike `list_program()`, this is
    a fixed personal-style result list, not the filterable program (consistent with the
    favorites/personal-schedule area, US-10).
    """
    if not artist_ids:
        return []
    rank = {artist_id: index for index, artist_id in enumerate(artist_ids)}
    rows = (
        db.query(
            Act.id,
            Artist.name.label("title"),
            Stage.name.label("stage"),
            Act.starts_at,
            Act.ends_at,
            Act.artist_id,
        )
        .join(Artist)
        .join(Stage)
        .filter(Act.artist_id.in_(artist_ids))
        .all()
    )
    return sorted(rows, key=lambda row: (rank[row.artist_id], row.starts_at))


def search_acts(db: Session, query_vector: list[float], limit: int = SEARCH_ARTIST_LIMIT):
    """Acts of the `limit` artists most similar to `query_vector` (B8), best artist match first.

    Combines `search_top_artists()` and `acts_for_artists()` - see there for details on ranking
    and on why only the latter has automated tests.
    """
    artist_ids = search_top_artists(db, query_vector, limit)
    return acts_for_artists(db, artist_ids)
