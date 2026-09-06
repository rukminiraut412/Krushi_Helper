import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables
load_dotenv()

# Read database URL without hardcoding credentials
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://krushirakshak:krushirakshak_secret@localhost:5432/krushirakshak_db"
)

# Initialize SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session and safely closing on completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """
    Executes a lightweight query to verify the database connection health.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                return {
                    "connected": True,
                    "database": "PostgreSQL",
                    "status": "online"
                }
            return {
                "connected": False,
                "error": "Unexpected scalar query result"
            }
    except Exception as exc:
        return {
            "connected": False,
            "error": str(exc)
        }
