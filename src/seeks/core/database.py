from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from seeks.utils.get_home_dir import get_home_dir

# Create a database file in the user's home directory
database_file = get_home_dir() / "database.db"
engine = create_engine(f"sqlite:///{database_file}", echo=False)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Utility function to get database session
def get_session() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
