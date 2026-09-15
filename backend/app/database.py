import logging
from sqlalchemy import create_engine
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
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info(f"Connected to database: {db_url}")
except Exception as e:
    logger.warning(f"Failed to connect to primary database ({db_url}): {e}. Falling back to SQLite.")
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
