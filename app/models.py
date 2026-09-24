"""ORM models: Artist, Stage, Act (see doc/domain-model.md)."""
from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base

# Length of Artist.embedding, fixed by the embedding model
# sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2. Vectors of different models are
# not comparable, so changing the model means a new dimension and re-embedding every artist.
EMBEDDING_DIM = 384


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # name, genre and description together are the text the semantic search compares against.
    genre = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    # Derived from name, genre and description, never edited by hand. Stays NULL until the
    # embeddings are generated (vector search, roadmap step 8).
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    acts = relationship("Act", back_populates="artist")

    __table_args__ = (
        CheckConstraint("trim(name) <> ''", name="ck_artists_name_not_empty"),
        CheckConstraint("trim(genre) <> ''", name="ck_artists_genre_not_empty"),
        CheckConstraint("trim(description) <> ''", name="ck_artists_description_not_empty"),
    )


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    acts = relationship("Act", back_populates="stage")

    __table_args__ = (
        CheckConstraint("trim(name) <> ''", name="ck_stages_name_not_empty"),
    )


class Act(Base):
    __tablename__ = "acts"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)

    artist = relationship("Artist", back_populates="acts")
    stage = relationship("Stage", back_populates="acts")

    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_acts_ends_after_starts"),
    )
