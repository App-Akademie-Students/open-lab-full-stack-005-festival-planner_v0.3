"""ORM models: Artist, Stage, Act (see doc/domain-model.md)."""
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    acts = relationship("Act", back_populates="artist")

    __table_args__ = (
        CheckConstraint("trim(name) <> ''", name="ck_artists_name_not_empty"),
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
