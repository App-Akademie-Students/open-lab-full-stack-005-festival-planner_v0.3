"""Tests for app.embeddings: embedding text and storing embeddings.

The real model is not loaded (PyTorch import and a ~470 MB download); `embed_artists` gets a fake
encoder instead. Runs against in-memory SQLite like test_models.py - storing and reading a vector
works there, vector search does not.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.embeddings import artist_embedding_text, embed_artists
from app.models import EMBEDDING_DIM, Artist


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


def test_embedding_text_combines_name_genre_and_description():
    artist = Artist(name="Ambient Drift", genre="Ambient", description="Schwebende Klangflächen.")

    assert artist_embedding_text(artist) == "Ambient Drift. Genre: Ambient. Schwebende Klangflächen."


def test_embedding_text_ignores_surrounding_whitespace():
    padded = Artist(name=" Ambient Drift ", genre="Ambient\n", description="  Schwebend.")
    clean = Artist(name="Ambient Drift", genre="Ambient", description="Schwebend.")

    assert artist_embedding_text(padded) == artist_embedding_text(clean)


@pytest.mark.parametrize("field", ["name", "genre", "description"])
def test_embedding_text_changes_with_every_field(field):
    # Every field is part of the text, so changing any of them requires a new embedding.
    original = Artist(name="Jazz Corner", genre="Jazz", description="Entspannt.")
    changed = Artist(name="Jazz Corner", genre="Jazz", description="Entspannt.")
    setattr(changed, field, "anders")

    assert artist_embedding_text(changed) != artist_embedding_text(original)


def fake_encode(texts):
    # Distinct, recognizable vector per text position: [1.0, ...], [2.0, ...], ...
    return [[float(position + 1)] * EMBEDDING_DIM for position in range(len(texts))]


def test_embed_artists_stores_one_vector_per_artist(db):
    db.add_all(
        [
            Artist(name="Folk Trio", genre="Folk", description="Akustisch."),
            Artist(name="Bass Drop", genre="Drum and Bass", description="Laut."),
        ]
    )
    db.commit()

    assert embed_artists(db, encode=fake_encode) == 2

    artists = db.query(Artist).order_by(Artist.id).all()
    assert [artist.embedding[0] for artist in artists] == [1.0, 2.0]
    assert all(len(artist.embedding) == EMBEDDING_DIM for artist in artists)


def test_embed_artists_uses_the_embedding_text(db):
    db.add(Artist(name="Folk Trio", genre="Folk", description="Akustisch."))
    db.commit()
    received = []

    def recording_encode(texts):
        received.extend(texts)
        return fake_encode(texts)

    embed_artists(db, encode=recording_encode)

    assert received == ["Folk Trio. Genre: Folk. Akustisch."]


def test_embed_artists_replaces_outdated_embeddings(db):
    db.add(Artist(name="Folk Trio", genre="Folk", description="Akustisch.", embedding=[9.0] * EMBEDDING_DIM))
    db.commit()

    embed_artists(db, encode=fake_encode)

    assert db.query(Artist).one().embedding[0] == 1.0
