import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.core.config import settings
from src.core.database import Base, get_db

# Use a separate test database or same with cleanup
# For simplicity, we use same but in a transaction that rolls back or we just create/drop tables.
# Ideally: Create a temporary test DB. Here we assume we are okay running against the configured DB 
# (which should be a test one in CI).

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # Rollback happens automatically when session closes or we explicit rollback?
        # Actually with async_sessionmaker it commits if you tell it to.
        # For tests, we might want to truncate tables or rollback transaction.
        # Here we rely on dropped tables at end of session for cleanup if scope was session, 
        # but for function scope we want isolation. 
        # Simplest Strategy: Truncate tables after each test OR use nested transaction.
        await session.rollback()

@pytest.fixture(scope="function")
async def client(db) -> AsyncGenerator[AsyncClient, None]:
    # Override dependency
    async def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()
