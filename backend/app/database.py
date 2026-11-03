import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger("resume_ai")

db_url = settings.DATABASE_URL
connect_args = {}

try:
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(db_url, connect_args=connect_args)
    with engine.connect() as conn:
        pass
    logger.info("Connected to database: %s", make_url(db_url).render_as_string(hide_password=True))
except Exception as e:
    if not db_url.startswith("sqlite"):
        raise RuntimeError(
            f"Could not connect to configured database "
            f"{make_url(db_url).render_as_string(hide_password=True)}"
        ) from e

    logger.warning(
        "Failed to connect to primary database (%s): %s. Falling back to SQLite.",
        make_url(db_url).render_as_string(hide_password=True),
        e,
    )
    db_url = settings.SQLITE_FALLBACK_URL
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
