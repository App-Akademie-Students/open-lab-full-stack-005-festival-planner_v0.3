"""Database infrastructure: engine, session factory, Base, init_db()."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # No silent fallback: a default would hide a misconfiguration at runtime.
    raise RuntimeError(
        "DATABASE_URL is not set. Create a .env file in the project folder containing "
        "DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require "
        "(see CLAUDE.md, 'Configure database connection')."
    )

# Force the psycopg (v3) driver; a bare "postgresql://" URL defaults to psycopg2.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# pool_pre_ping: Neon suspends its compute when idle, which leaves stale
# connections in the pool. Without the check, the first request after a pause
# fails; with it, SQLAlchemy discards the dead connection and opens a new one.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
