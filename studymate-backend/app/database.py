from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


encoded_password = quote_plus(settings.db_password)

DATABASE_URL = (
    f"mysql+pymysql://{settings.db_user}:{encoded_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    "?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def test_database_connection() -> dict:
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT DATABASE()")
            ).scalar()

            tables = connection.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = :database_name
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                ),
                {"database_name": settings.db_name},
            ).scalars().all()

        return {
            "connected": True,
            "database": database_name,
            "tables": tables,
            "table_count": len(tables),
        }

    except Exception as error:
        return {
            "connected": False,
            "error": str(error),
        }