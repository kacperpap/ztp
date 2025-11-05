# src/lab_01/database.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# project root: 2 levels up from src/lab_01 -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# domyślna ścieżka plikowej bazy SQLite w katalogu projektu
DEFAULT_DB_PATH = PROJECT_ROOT / "lab01.db"

# allow override via env var, e.g. for tests
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# sqlite needs check_same_thread=False when using sessions across threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

# Dependency generator for FastAPI routes
def get_db():
    """
    Yields a SQLAlchemy session and ensures it's closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
