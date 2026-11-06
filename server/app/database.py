from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# foundation for sqlalchemy models
class Base(DeclarativeBase):
    pass


# manages connections to postgresql
engine = create_engine(settings.DATABASE_URL)

# creates database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# provides a session to an api endpoint and closes it after
def get_db() -> Generator:
    db = SessionLocal()  # create a new database session

    try:
        yield db  # provide session to endpoint
    except Exception:
        db.rollback()  # revert transaction
        raise
    finally:
        db.close()  # ensure session is closed
