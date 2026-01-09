from sqlmodel import create_engine, SQLModel, Session
from pathlib import Path
import os

# Use DATABASE_URL env var if provided (Postgres for production); default to SQLite demo DB
default_sqlite = f"sqlite:///{Path(__file__).resolve().parents[1] / 'data.db'}"
DB_URL = os.environ.get("DATABASE_URL", default_sqlite)
engine = create_engine(DB_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
