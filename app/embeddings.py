"""Artist embeddings for the semantic search (vector search phase 1, see doc/architecture.md).

Run with `python -m app.embeddings` after `python -m app.seed`: it (re)generates the embedding
of every artist. The embedding text is built only here (`artist_embedding_text`), so every
artist is embedded the same way, and the later search uses the same model (`MODEL_NAME`).
"""
from collections.abc import Callable
from functools import lru_cache

from sqlalchemy.orm import Session

from app import crud
from app.models import EMBEDDING_DIM, Artist

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def artist_embedding_text(artist: Artist) -> str:
    """The text an artist is embedded from: name, genre and description, always in this form.

    Stage and times are deliberately not part of it (see B8 in doc/requirements.md).
    Changing this format changes every embedding, so all artists must be re-embedded then.
    """
    return f"{artist.name.strip()}. Genre: {artist.genre.strip()}. {artist.description.strip()}"


@lru_cache(maxsize=1)
def get_model():
    """The embedding model, loaded once per process.

    Imported here instead of at module level: sentence-transformers pulls in PyTorch, which takes
    many seconds to import. Only code that actually embeds pays for it, not the app start or tests.
    On the first run the model is downloaded from Hugging Face and cached locally.
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    dim = model.get_embedding_dimension()
    if dim != EMBEDDING_DIM:
        raise RuntimeError(
            f"{MODEL_NAME} returns {dim} dimensions, but Artist.embedding has {EMBEDDING_DIM}."
        )
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """One vector per text.

    Normalized to length 1, so cosine similarity and dot product give the same ranking - the
    search can use either pgvector operator.
    """
    vectors = get_model().encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]


def embed_artists(
    db: Session, encode: Callable[[list[str]], list[list[float]]] = embed_texts
) -> int:
    """(Re)generates and stores the embedding of every artist; returns how many.

    Always all artists, not only those without an embedding: an existing embedding may be
    outdated after name, genre or description changed. With a few dozen artists that is cheap.
    `encode` is replaceable so tests run without the real model.
    """
    artists = crud.list_artists(db)
    vectors = encode([artist_embedding_text(artist) for artist in artists])
    for artist, vector in zip(artists, vectors, strict=True):
        artist.embedding = vector
    db.commit()
    return len(artists)


if __name__ == "__main__":
    from app.db import SessionLocal

    session = SessionLocal()
    try:
        count = embed_artists(session)
    finally:
        session.close()
    print(f"Embeddings for {count} artists stored ({MODEL_NAME}, {EMBEDDING_DIM} dimensions).")
