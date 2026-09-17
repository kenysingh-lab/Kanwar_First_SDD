"""SQLAlchemy engine/session setup against a single SQLite file."""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# `python -m app.database` runs this file as `__main__`, which would otherwise
# make `models.py`'s `from .database import Base` re-import (and re-execute)
# this module under its real name, producing a second, disconnected `Base`
# whose tables never get created. Alias this already-running module in place
# so that relative import resolves back to it instead.
sys.modules.setdefault(f"{__package__}.database", sys.modules[__name__])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables and seed a default Admin account if none exists yet."""
    from . import models  # deferred import: models depends on Base above

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(models.Admin).first() is None:
            username = os.environ.get("ADMIN_USERNAME", "admin")
            password = os.environ.get("ADMIN_PASSWORD", "admin")
            admin = models.Admin(username=username, password_hash=models.hash_password(password))
            db.add(admin)
            db.commit()
            print(
                f"Created default Admin '{username}' with a default password — "
                "change it before relying on this for anything sensitive."
            )
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
        print(f"Initialized database at {DB_PATH}")
    else:
        print("Usage: python -m app.database init")
