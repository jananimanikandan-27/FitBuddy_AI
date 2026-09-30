from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL


# SQLite needs this option when used with FastAPI.
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)


Base = declarative_base()


def init_db():
    """
    Create all database tables.
    """
    # Import models here so SQLAlchemy knows about them.
    from . import models

    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI database dependency.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()