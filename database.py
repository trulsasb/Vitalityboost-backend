from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from models.base import Base
from utils.env import settings

DATABASE_URL = settings.DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _add_missing_columns():
    """create_all() only creates tables that don't exist yet -- it never
    alters an existing one, so a new column added to a model silently never
    reaches a live database that already has that table. This has broken
    production before (commit b86a594, "production-breaking schema drift"),
    fixed that time by hand-running SQL against the live DB. For every table
    that already exists, add whichever of its model's columns are missing
    from the live table. Additive only -- never drops, renames, or alters an
    existing column -- so it's safe to run on every startup. Only safe for
    columns that are nullable or have a server_default; a new NOT NULL
    column with no default would still need a one-off manual backfill."""

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue  # brand new table -- create_all() above already made it in full

            existing_columns = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue
                ddl_type = column.type.compile(dialect=engine.dialect)
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {ddl_type}'))


def init_db():
    Base.metadata.create_all(bind=engine)
    _add_missing_columns()
