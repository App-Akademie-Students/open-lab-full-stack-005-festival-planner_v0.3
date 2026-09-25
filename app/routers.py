"""API endpoints: GET /api/program, /api/stages, /api/days, /api/search, /api/answer."""
import logging
from collections.abc import Callable
from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud
from app.db import get_db
from app.embeddings import embed_texts
from app.llm import LLMUnavailableError, generate_answer, post_to_ollama
from app.schedule import compute_statuses, festival_day, festival_now

router = APIRouter()
logger = logging.getLogger(__name__)


class ProgramItemOut(BaseModel):
    id: int
    title: str
    stage: str
    starts_at: datetime
    ends_at: datetime
    status: str | None


class ProgramResponse(BaseModel):
    now: datetime
    items: list[ProgramItemOut]


class SearchResultOut(BaseModel):
    id: int
    title: str
    stage: str
    day: date
    starts_at: datetime
    ends_at: datetime


class SearchResponse(BaseModel):
    items: list[SearchResultOut]


class AnswerResponse(BaseModel):
    # ok: `answer` holds the generated text. no_hits: the search found nothing, so the LLM was
    # not asked (B10). unavailable: Ollama not reachable, too slow or unusable response (B10).
    status: Literal["ok", "no_hits", "unavailable"]
    answer: str | None


@router.get("/api/stages")
def get_stages(db: Session = Depends(get_db)) -> list[str]:
    return crud.list_stages(db)


@router.get("/api/days")
def get_days(db: Session = Depends(get_db)) -> list[date]:
    return crud.list_days(db)


@router.get("/api/program", response_model=ProgramResponse)
def get_program(
    stage: str | None = None,
    day: date | None = None,
    db: Session = Depends(get_db),
    now: datetime = Depends(festival_now),
) -> ProgramResponse:
    rows = crud.list_program(db, stage=stage, day=day)
    statuses = compute_statuses(rows, now)
    items = [
        ProgramItemOut(
            id=row.id,
            title=row.title,
            stage=row.stage,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
            status=status,
        )
        for row, status in zip(rows, statuses)
    ]
    return ProgramResponse(now=now, items=items)


def search_artist_ids(q: str = Query(min_length=1), db: Session = Depends(get_db)) -> list[int]:
    """Embeds `q` and ranks artists by similarity (B8, `crud.search_top_artists`).

    A FastAPI dependency, like `festival_now` - so tests can override it and skip both the real
    embedding model and pgvector (neither works under the SQLite test database), the same way
    `festival_now` is replaced by a fixed time. See tests/test_search_api.py.
    """
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="q must not be empty")
    query_vector = embed_texts([query])[0]
    return crud.search_top_artists(db, query_vector)


@router.get("/api/search", response_model=SearchResponse)
def search(
    artist_ids: list[int] = Depends(search_artist_ids), db: Session = Depends(get_db)
) -> SearchResponse:
    rows = crud.acts_for_artists(db, artist_ids)
    items = [
        SearchResultOut(
            id=row.id,
            title=row.title,
            stage=row.stage,
            day=festival_day(row.starts_at),
            starts_at=row.starts_at,
            ends_at=row.ends_at,
        )
        for row in rows
    ]
    return SearchResponse(items=items)


def llm_send() -> Callable[[dict], dict]:
    """How the LLM is called - a dependency so tests can replace Ollama, like `festival_now`."""
    return post_to_ollama


@router.get("/api/answer", response_model=AnswerResponse)
def answer(
    q: str = Query(min_length=1),
    artist_ids: list[int] = Depends(search_artist_ids),
    db: Session = Depends(get_db),
    now: datetime = Depends(festival_now),
    send: Callable[[dict], dict] = Depends(llm_send),
) -> AnswerResponse:
    """Generated answer to `q` (C12, B10), based only on the hits /api/search returns for `q`.

    A separate endpoint instead of a field on /api/search: the answer is only requested on
    demand (F12, "Antwort generieren") and can take up to the LLM timeout, while the search
    must stay fast. The search runs again here - cheap compared to the LLM call. `q` is
    validated (non-empty after trimming) by `search_artist_ids`, same as /api/search.
    Always 200: "no answer" is a normal outcome the frontend shows as a hint, not an error.
    """
    rows = crud.acts_for_artists(db, artist_ids)
    if not rows:
        return AnswerResponse(status="no_hits", answer=None)
    try:
        text = generate_answer(q.strip(), rows, now, send)
    except LLMUnavailableError as error:
        logger.warning("Generated answer unavailable: %s", error)
        return AnswerResponse(status="unavailable", answer=None)
    return AnswerResponse(status="ok", answer=text)
