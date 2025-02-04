from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from seeks.utils.get_home_dir import get_home_dir


# Define base class for declarative base to potentially add common methods
class Base(DeclarativeBase):
    pass


# Create a database file in the user's home directory
db_file = get_home_dir() / "database.db"
db_file.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{db_file}", echo=False)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Utility function to get database session
def get_database() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
