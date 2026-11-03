from pathlib import Path

from sqlalchemy import MetaData, create_engine, inspect, select
from sqlalchemy.engine import Engine, URL

from app.database import Base, engine as mysql_engine
from app.models import models


SQLITE_PATH = Path(__file__).resolve().parent / "resume_ai.db"
BATCH_SIZE = 500


def migrate(source_path: Path = SQLITE_PATH, target_engine: Engine = mysql_engine):
    if not source_path.exists():
        raise FileNotFoundError(f"SQLite source database not found: {source_path}")

    source_engine = create_engine(URL.create("sqlite", database=str(source_path)))
    source_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)
    source_tables = set(source_metadata.tables)

    Base.metadata.create_all(bind=target_engine)
    target_inspector = inspect(target_engine)
    populated_tables = [
        table.name
        for table in Base.metadata.sorted_tables
        if target_inspector.has_table(table.name)
        and _table_has_rows(target_engine, table)
    ]
    if populated_tables:
        raise RuntimeError(
            "MySQL app tables are not empty; refusing to risk duplicate data. "
            f"Non-empty tables: {', '.join(populated_tables)}"
        )

    migrated_counts = {}
    with source_engine.connect() as source, target_engine.begin() as target:
        for table in Base.metadata.sorted_tables:
            if table.name not in source_tables:
                continue

            source_table = source_metadata.tables[table.name]
            source_columns = set(source_table.columns.keys())
            shared_columns = [column.name for column in table.columns if column.name in source_columns]
            if not shared_columns:
                continue

            result = source.execute(select(*(source_table.c[name] for name in shared_columns)))
            copied = 0
            while rows := result.fetchmany(BATCH_SIZE):
                records = [
                    {name: row._mapping[name] for name in shared_columns}
                    for row in rows
                ]
                target.execute(table.insert(), records)
                copied += len(records)
            migrated_counts[table.name] = copied

    source_engine.dispose()
    print("SQLite data migration completed.")
    for table_name, count in migrated_counts.items():
        print(f"{table_name}: {count} rows")


def _table_has_rows(connection_engine: Engine, table):
    with connection_engine.connect() as connection:
        return connection.execute(select(table).limit(1)).first() is not None


if __name__ == "__main__":
    migrate()
