"""Tests for app/llm.py: context text, chat messages and the Ollama call for the generated answer.

No database and no running Ollama: the HTTP call is replaced by a fake `send` or a patched
`urlopen`, like the fake encoder in tests/test_embeddings.py.
"""
import json
import urllib.error
from datetime import datetime
from types import SimpleNamespace

import pytest

from app import llm
from app.llm import (
    MODEL_NAME,
    SYSTEM_PROMPT,
    TIMEOUT_SECONDS,
    LLMUnavailableError,
    build_context,
    build_messages,
    chat,
    format_time,
    generate_answer,
    post_to_ollama,
)

NOW = datetime(2026, 9, 26, 15, 30)  # Samstag


def hit(title: str, starts_at: datetime, ends_at: datetime, stage: str = "Hauptbühne"):
    """A search hit shaped like a row from crud.acts_for_artists()."""
    return SimpleNamespace(
        title=title,
        genre=f"Genre {title}",
        description=f"Beschreibung {title}.",
        stage=stage,
        starts_at=starts_at,
        ends_at=ends_at,
    )


def titles_in_order(context: str) -> list[str]:
    lines = context.splitlines()
    return [line.removeprefix("Artist: ") for line in lines if line.startswith("Artist: ")]


def test_format_time_writes_out_weekday():
    assert (
        format_time(datetime(2026, 9, 27, 15, 30), datetime(2026, 9, 27, 17, 0))
        == "Sonntag, 27.09., 15:30–17:00"
    )


def test_format_time_past_midnight_keeps_start_day():
    assert (
        format_time(datetime(2026, 9, 25, 23, 0), datetime(2026, 9, 26, 1, 0))
        == "Freitag, 25.09., 23:00–01:00"
    )


def test_build_context_block_contains_all_fields():
    context = build_context(
        [hit("Brass Explosion", datetime(2026, 9, 27, 15, 30), datetime(2026, 9, 27, 17, 0))], NOW
    )

    assert context == (
        "Gefundene Acts:\n\n"
        "1.\n"
        "Artist: Brass Explosion\n"
        "Genre: Genre Brass Explosion\n"
        "Beschreibung: Beschreibung Brass Explosion.\n"
        "Bühne: Hauptbühne\n"
        "Zeit: Sonntag, 27.09., 15:30–17:00\n"
        "Status: kommt noch"
    )


def test_build_context_labels_each_status():
    context = build_context(
        [
            hit("Running", datetime(2026, 9, 26, 15, 0), datetime(2026, 9, 26, 16, 30)),
            hit("Upcoming", datetime(2026, 9, 26, 23, 0), datetime(2026, 9, 27, 1, 0)),
            hit("Past", datetime(2026, 9, 26, 12, 0), datetime(2026, 9, 26, 13, 0)),
        ],
        NOW,
    )

    assert "Artist: Running\n" in context and "Status: läuft gerade" in context
    assert "Status: kommt noch" in context
    assert "Status: vorbei" in context


def test_build_context_puts_past_acts_last_and_keeps_rank_within_groups():
    rows = [
        hit("Past 1", datetime(2026, 9, 26, 12, 0), datetime(2026, 9, 26, 13, 0)),
        hit("Upcoming 2", datetime(2026, 9, 27, 15, 30), datetime(2026, 9, 27, 17, 0)),
        hit("Past 3", datetime(2026, 9, 25, 16, 30), datetime(2026, 9, 25, 17, 30)),
        hit("Running 4", datetime(2026, 9, 26, 15, 0), datetime(2026, 9, 26, 16, 30)),
    ]

    context = build_context(rows, NOW)

    assert titles_in_order(context) == ["Upcoming 2", "Running 4", "Past 1", "Past 3"]
    assert context.index("1.\nArtist: Upcoming 2") < context.index("4.\nArtist: Past 3")


def test_build_messages_system_rules_then_context_and_question_last():
    rows = [hit("Brass Explosion", datetime(2026, 9, 27, 15, 30), datetime(2026, 9, 27, 17, 0))]

    messages = build_messages("Wo gibt es Blasmusik?", rows, NOW)

    assert [message["role"] for message in messages] == ["system", "user"]
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[1]["content"].startswith("Gefundene Acts:\n\n1.\nArtist: Brass Explosion")
    assert messages[1]["content"].endswith("\n\nFrage: Wo gibt es Blasmusik?")


def fake_send(answer):
    """A `send` replacement that records the request body and returns an Ollama-like response."""
    sent = []

    def send(body):
        sent.append(body)
        return {"message": {"role": "assistant", "content": answer}}

    send.sent = sent
    return send


def test_chat_returns_stripped_answer_and_sends_settings():
    send = fake_send("  Brass Explosion spielt am Sonntag.\n")
    messages = [{"role": "user", "content": "Frage"}]

    answer = chat(messages, send)

    assert answer == "Brass Explosion spielt am Sonntag."
    [body] = send.sent
    assert body["model"] == MODEL_NAME
    assert body["messages"] == messages
    assert body["stream"] is False
    assert body["think"] is False
    assert body["options"] == {"temperature": 0.2}


@pytest.mark.parametrize("response", [{}, {"message": {}}, {"message": None}, {"error": "x"}])
def test_chat_unexpected_response_is_unavailable(response):
    with pytest.raises(LLMUnavailableError):
        chat([{"role": "user", "content": "Frage"}], lambda body: response)


def test_chat_empty_answer_is_unavailable():
    with pytest.raises(LLMUnavailableError):
        chat([{"role": "user", "content": "Frage"}], fake_send("   "))


def test_generate_answer_sends_context_built_from_hits():
    send = fake_send("Antwort")
    rows = [hit("Brass Explosion", datetime(2026, 9, 27, 15, 30), datetime(2026, 9, 27, 17, 0))]

    assert generate_answer("Wo gibt es Blasmusik?", rows, NOW, send) == "Antwort"
    assert send.sent[0]["messages"] == build_messages("Wo gibt es Blasmusik?", rows, NOW)


def test_generate_answer_without_hits_does_not_call_the_llm():
    send = fake_send("Antwort")

    with pytest.raises(ValueError):
        generate_answer("Frage", [], NOW, send)
    assert send.sent == []


class FakeResponse:
    """Stands in for the object urlopen() returns (a context manager with a body)."""

    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, *args):
        return self.body


def test_post_to_ollama_sends_json_with_timeout(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse(b'{"message": {"content": "ok"}}')

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)

    assert post_to_ollama({"model": "m"}) == {"message": {"content": "ok"}}
    [(request, timeout)] = calls
    assert timeout == TIMEOUT_SECONDS
    assert request.full_url == llm.OLLAMA_CHAT_URL
    assert json.loads(request.data) == {"model": "m"}


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.URLError(ConnectionRefusedError()),  # Ollama not running
        TimeoutError("timed out"),  # slower than TIMEOUT_SECONDS
        urllib.error.HTTPError(llm.OLLAMA_CHAT_URL, 404, "model not found", None, None),
    ],
)
def test_post_to_ollama_failures_are_unavailable(monkeypatch, error):
    def fake_urlopen(request, timeout):
        raise error

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(LLMUnavailableError):
        post_to_ollama({"model": "m"})


def test_post_to_ollama_invalid_json_is_unavailable(monkeypatch):
    monkeypatch.setattr(
        llm.urllib.request, "urlopen", lambda request, timeout: FakeResponse(b"<html>")
    )

    with pytest.raises(LLMUnavailableError):
        post_to_ollama({"model": "m"})
