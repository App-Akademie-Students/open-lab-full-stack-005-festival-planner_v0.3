"""Generated answer from search hits (vector search phase 2, LLM/RAG, see doc/architecture.md).

The retrieval layer is the existing semantic search (B8); this module turns its hits into the
prompt for the LLM and asks the LLM (Ollama, running locally - T5). The context text is built
only here (`build_context`), like the embedding text in `app/embeddings.py`, so format and
status are covered by tests.

Ollama is called over its HTTP API with `urllib` from the standard library, so no extra
dependency is needed for a single POST request.
"""
import json
import urllib.request
from collections.abc import Callable
from datetime import datetime

from app.schedule import act_phase, festival_day

OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen3-instruct:4b"
# Low temperature: as little embellishment as possible (roadmap phase 2 step 6).
TEMPERATURE = 0.2
# Answers took 2-35 s on the dev machine, plus ~8 s model loading on the first call (step 6).
TIMEOUT_SECONDS = 60


class LLMUnavailableError(Exception):
    """No generated answer: Ollama not reachable, too slow, or an unusable response.

    The caller shows "not available" instead of an answer; the search itself is unaffected (B10).
    """


# Refined in roadmap phase 2 step 6 (prompt variant v2) - see doc/architecture.md for the
# reason behind every rule. German on purpose: the answer must be German (T5).
SYSTEM_PROMPT = """Du bist ein Assistent für einen Festivalplaner.

Beantworte die Frage ausschließlich anhand des bereitgestellten Kontexts.

Erfinde keine Künstler, Genres, Bühnen oder Auftrittszeiten.

Wenn die Informationen nicht ausreichen, sage dies ausdrücklich.

Beachte den Status jedes Acts:
- „kommt noch" und „läuft gerade": diese Acts kannst du empfehlen.
- „vorbei": empfiehl diesen Act nicht. Wenn du ihn trotzdem nennst, schreibe dazu, dass er schon vorbei ist.

Ein Act passt nur zur Frage, wenn sein Genre oder seine Beschreibung ausdrücklich dazu passt. Nenne nur passende Acts und lass die anderen weg.

Nenne Acts beim Namen, nicht über ihre Nummer, jeweils mit Tag, Uhrzeit und Bühne.

Antworte auf Deutsch in höchstens drei Sätzen, als Fließtext ohne Formatierung."""

# Written out instead of "Fr"/"Sa"/"So": in step 6 the model read "So" as "Samstag".
# Built by hand (index = date.weekday(), Monday first) - no locale dependency.
WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

PHASE_LABELS = {"running": "läuft gerade", "upcoming": "kommt noch", "past": "vorbei"}


def format_time(starts_at: datetime, ends_at: datetime) -> str:
    """'Samstag, 26.09., 12:00–13:00' - the festival day an act starts on, then start and end.

    An act past midnight keeps its start day and simply shows the earlier end time
    ('Freitag, 25.09., 23:00–01:00'), like the program list does.
    """
    day = festival_day(starts_at)
    return (
        f"{WEEKDAYS[day.weekday()]}, {day:%d.%m.}, "
        f"{starts_at:%H:%M}–{ends_at:%H:%M}"
    )


def build_context(rows, now: datetime) -> str:
    """The search hits as the text block the LLM answers from.

    `rows` are search hits as returned by `crud.acts_for_artists()` (best match first).
    Running and upcoming acts come before past ones, rank order kept within each group: in
    step 6 the model kept recommending a past act that was listed first, despite the status
    rule in the prompt. Past acts stay in the context so "Wann hat X gespielt?" still works.
    """
    phases = [act_phase(row.starts_at, row.ends_at, now) for row in rows]
    # sorted() is stable, so within each group the original (rank) order is kept.
    ordered = sorted(zip(rows, phases), key=lambda pair: pair[1] == "past")
    blocks = [
        f"{number}.\n"
        f"Artist: {row.title}\n"
        f"Genre: {row.genre}\n"
        f"Beschreibung: {row.description}\n"
        f"Bühne: {row.stage}\n"
        f"Zeit: {format_time(row.starts_at, row.ends_at)}\n"
        f"Status: {PHASE_LABELS[phase]}"
        for number, (row, phase) in enumerate(ordered, start=1)
    ]
    return "Gefundene Acts:\n\n" + "\n\n".join(blocks)


def build_messages(question: str, rows, now: datetime) -> list[dict[str, str]]:
    """Chat messages for the LLM: rules as system message, context then question as user message.

    The question comes last, right before the model's answer. Only called with at least one hit:
    without hits there is no LLM call at all (B10).
    """
    user_message = f"{build_context(rows, now)}\n\nFrage: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def post_to_ollama(body: dict) -> dict:
    """POSTs `body` to Ollama's chat endpoint and returns the decoded JSON response.

    Every failure becomes LLMUnavailableError: connection refused (Ollama not running),
    HTTP errors (e.g. model not pulled), the timeout, and a response that is not JSON.
    """
    request = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    # URLError/HTTPError and TimeoutError are OSErrors; invalid JSON is a ValueError.
    except (OSError, ValueError) as error:
        raise LLMUnavailableError(f"Ollama request failed: {error}") from error


def chat(messages: list[dict[str, str]], send: Callable[[dict], dict] = post_to_ollama) -> str:
    """The LLM's answer to `messages`, stripped. Raises LLMUnavailableError if there is none.

    `send` is replaceable so tests run without Ollama (like `encode` in `embed_artists()`).
    """
    body = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        # qwen3 can "think" before answering; that only costs time here and must not end up
        # in the answer.
        "think": False,
        "options": {"temperature": TEMPERATURE},
    }
    response = send(body)
    try:
        answer = response["message"]["content"].strip()
    except (KeyError, TypeError, AttributeError) as error:
        raise LLMUnavailableError(f"Unexpected Ollama response: {response!r}") from error
    if not answer:
        raise LLMUnavailableError("Ollama returned an empty answer")
    return answer


def generate_answer(
    question: str, rows, now: datetime, send: Callable[[dict], dict] = post_to_ollama
) -> str:
    """The generated answer (B10) to `question`, based only on the search hits `rows`.

    `rows` must not be empty: without hits there is no LLM call at all (B10) - the caller
    checks that before. Raises LLMUnavailableError if the LLM gives no usable answer.
    """
    if not rows:
        raise ValueError("generate_answer() needs at least one search hit")
    return chat(build_messages(question, rows, now), send)
