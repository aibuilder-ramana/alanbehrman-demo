import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DB_URL = os.getenv("DB_URL", "postgresql://localhost:5432/elevia_alanbehrman")


def _pin_driver(url: str) -> str:
    """Name the driver explicitly.

    SQLAlchemy 2.1 changed the default DBAPI for a bare "postgresql://" URL
    from psycopg2 to psycopg (v3). This project installs psycopg2-binary, so
    a bare URL resolves to a driver that is not present and the app dies on
    import. Saying psycopg2 outright keeps it working on either version.
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):  # legacy scheme some providers still emit
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url


engine = create_engine(_pin_driver(DB_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
