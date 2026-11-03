import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine import URL

from app.database import Base
from app.models import models
from migrate_sqlite_to_mysql import migrate


def test_migrate_copies_rows_and_prevents_duplicates(tmp_path):
    source_path = tmp_path / "source.db"
    source_engine = create_engine(URL.create("sqlite", database=str(source_path)))
    Base.metadata.create_all(source_engine)

    with source_engine.begin() as connection:
        connection.execute(
            models.User.__table__.insert(),
            {
                "id": 77,
                "full_name": "Test Candidate",
                "email": "migration-test@example.com",
                "hashed_password": "not-a-real-password",
            },
        )
    source_engine.dispose()

    target_engine = create_engine("sqlite://")
    migrate(source_path, target_engine)

    with target_engine.connect() as connection:
        row = connection.execute(
            select(models.User.full_name).where(models.User.id == 77)
        ).scalar_one()
        assert row == "Test Candidate"

    with pytest.raises(RuntimeError, match="not empty"):
        migrate(source_path, target_engine)
