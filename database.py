from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

from models.base import Base  # bruk felles Base for ALLE modeller

DATABASE_URL = os.getenv("DATABASE_URL")

# Render krever NullPool + SSL
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
