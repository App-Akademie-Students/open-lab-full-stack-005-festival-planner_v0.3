"""Generated answer from search hits (vector search phase 2, LLM/RAG, see doc/architecture.md).

The retrieval layer is the existing semantic search (B8); this module turns its hits into the
prompt for the LLM and asks the LLM (Ollama, running locally - T5). The context text is built
only here (`build_context`), like the embedding text in `app/embeddings.py`, so format and
status are covered by tests.

Ollama is called over its HTTP API with `urllib` from the standard library, so no extra
dependency is needed for a single POST request.
"""
import json
import os
import re
import urllib.request
from collections.abc import Iterable
from collections.abc import Callable
from datetime import datetime

from dotenv import load_dotenv

from app.schedule import act_phase, festival_day

load_dotenv()

# Where Ollama runs and which model it uses come from .env (OLLAMA_URL, OLLAMA_MODEL).
# Unlike DATABASE_URL, both have defaults: the LLM is optional (B10), and the app and tests
# must work without these entries. OLLAMA_URL must stay a local Ollama (T5).
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_CHAT_URL = f"{OLLAMA_URL}/api/chat"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3-instruct:4b")
# Low temperature: as little embellishment as possible (roadmap phase 2 step 6).
TEMPERATURE = 0.2
# Answers took 2-35 s on the dev machine, plus ~8 s model loading on the first call (step 6).
TIMEOUT_SECONDS = 60


class LLMUnavailableError(Exception):
    """No generated answer: Ollama not reachable, too slow, or an unusable response.

    The caller shows "not available" instead of an answer; the search itself is unaffected (B10).
    """


class UngroundedAnswerError(LLMUnavailableError):
    """The LLM answered, but the answer states facts that are not in its context (B10).

    A subclass of LLMUnavailableError on purpose: a wrong answer is worse than none, so the
    caller treats it exactly like an unavailable LLM.
    """


# Refined in roadmap phase 2 steps 6 and 11 - see doc/architecture.md for the reason behind
# every rule. German on purpose: the answer must be German (T5).
SYSTEM_PROMPT = """Du bist ein Assistent für einen Festivalplaner.

Beantworte die Frage ausschließlich anhand des bereitgestellten Kontexts.

Erfinde keine Künstler, Genres, Bühnen oder Auftrittszeiten.

Wenn die Informationen nicht ausreichen, sage dies ausdrücklich.

Beachte den Status jedes Acts:
- „kommt noch" und „läuft gerade": diese Acts kannst du empfehlen.
- „vorbei": empfiehl diesen Act nicht. Wenn du ihn trotzdem nennst, schreibe dazu, dass er schon vorbei ist.

Ein Act passt nur zur Frage, wenn sein Genre oder seine Beschreibung ausdrücklich dazu passt. Nenne nur passende Acts und lass die anderen weg.

Schreibe einem Act nur Eigenschaften zu, die wörtlich in seinem Genre oder seiner Beschreibung stehen. Wenn nur ein Act passt, nenne nur diesen einen.

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


TIME_PATTERN = re.compile(r"\b(\d{1,2}):(\d{2})\b")  # 15:30, 1:00
DATE_PATTERN = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.")  # 26.09.
# A past act may be mentioned (e.g. "Wann hat X gespielt?") - but only marked as past.
PAST_MARKERS = ("vorbei", "gespielt", "stattgefunden")
# Claims that something is on right now - only true if one of the hits is running.
RUNNING_CLAIMS = ("läuft gerade", "gerade läuft", "läuft jetzt", "jetzt läuft")


def find_ungrounded(
    answer: str, rows, now: datetime, artist_names: Iterable[str], stage_names: Iterable[str]
) -> list[str]:
    """Facts in `answer` that its context (the search hits `rows`) does not back; [] if none.

    A deterministic check after the LLM call (roadmap phase 2 step 11), because the prompt
    alone does not stop the 4B model from mixing things up. It checks what can be checked
    exactly: acts and stages (against all known names, so one outside the hits is caught),
    times, dates and weekdays, a past act presented without being marked as past, and
    "läuft gerade" although none of the hits is running.
    Invented properties ("… auch mit Blasinstrumenten") cannot be caught this way.
    """
    problems = []

    hit_titles = {row.title for row in rows}
    for name in artist_names:
        if name in answer and name not in hit_titles:
            problems.append(f"act not in hits: {name}")
    hit_stages = {row.stage for row in rows}
    for name in stage_names:
        if name in answer and name not in hit_stages:
            problems.append(f"stage not in hits: {name}")

    # Start and end of every hit; an act past midnight also brings its end date and weekday.
    moments = [moment for row in rows for moment in (row.starts_at, row.ends_at)]
    times = {(moment.hour, moment.minute) for moment in moments}
    for hour, minute in TIME_PATTERN.findall(answer):
        if (int(hour), int(minute)) not in times:
            problems.append(f"time not in hits: {hour}:{minute}")
    dates = {(moment.day, moment.month) for moment in moments}
    for day, month in DATE_PATTERN.findall(answer):
        if (int(day), int(month)) not in dates:
            problems.append(f"date not in hits: {day}.{month}.")
    weekdays = {WEEKDAYS[moment.weekday()] for moment in moments}
    for name in WEEKDAYS:
        if name in answer and name not in weekdays:
            problems.append(f"weekday not in hits: {name}")

    past_titles = [
        row.title
        for row in rows
        if row.title in answer and act_phase(row.starts_at, row.ends_at, now) == "past"
    ]
    if past_titles and not any(marker in answer for marker in PAST_MARKERS):
        problems.append(f"past act not marked as past: {', '.join(past_titles)}")

    nothing_running = all(act_phase(row.starts_at, row.ends_at, now) != "running" for row in rows)
    if nothing_running and any(claim in answer for claim in RUNNING_CLAIMS):
        problems.append("claims an act is running, but none of the hits is")
    return problems


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
    question: str,
    rows,
    now: datetime,
    artist_names: Iterable[str] = (),
    stage_names: Iterable[str] = (),
    send: Callable[[dict], dict] = post_to_ollama,
) -> str:
    """The generated answer (B10) to `question`, based only on the search hits `rows`.

    `rows` must not be empty: without hits there is no LLM call at all (B10) - the caller
    checks that before. `artist_names`/`stage_names` are all known names, for the grounding
    check (`find_ungrounded`). Raises LLMUnavailableError if the LLM gives no usable answer,
    and its subclass UngroundedAnswerError if the answer states facts not in the hits.
    """
    if not rows:
        raise ValueError("generate_answer() needs at least one search hit")
    answer = chat(build_messages(question, rows, now), send)
    problems = find_ungrounded(answer, rows, now, artist_names, stage_names)
    if problems:
        raise UngroundedAnswerError(f"{'; '.join(problems)} - answer: {answer!r}")
    return answer
