
from app.config.settings import get_settings
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from typing import Generator


settings = get_settings()

# pre_ping
#  Protect against stale/dead connections

# recycle=3600
# Replace connections after 1 hour

# pool_size=20
# Keep 20 persistent connections

# max_overflow=0ho
# Never exceed those 20 connections

engine = create_engine(settings.DATABASE_URI,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_size=20,
                    max_overflow=0
                       )

# autocommit=False
# This means SQLAlchemy won't automatically commit your database changes.
# autoflush=False
# This controls when pending changes are automatically flushed to the database.
# Don't automatically push pending changes at every opportunity

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# You use Base when creating your models. class User(Base):
# your User becomes a SQLAlchemy ORM model.

Base = declarative_base()

def get_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


