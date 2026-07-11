from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Engine configuration (Postgres/SQLite)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # Enable multi-thread accessibility for sqlite MVP
    connect_args = {"check_same_thread": False}

# Sync Engine and Sessionmaker
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine and Sessionmaker
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Sync Database session generator (FastAPI Dependency)
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async Database session generator (FastAPI Dependency)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
