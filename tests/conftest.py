# tests/conftest.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.db_models import Base 
from app.core.config import settings
from app.core.logging_config import setup_logging

from fastapi.testclient import TestClient 
from app.main import app

logger = setup_logging()

# Test database URL - #TODO maybe move this to settings
TEST_DATABASE_URL = settings.test_database_url 

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_engine():
    """Create a test database engine."""
    # Convert PostgresDsn to string
    database_url = str(settings.test_database_url)

    engine = create_async_engine(
        database_url,
        echo=False, # Set to True for SQL Debugging
        pool_pre_ping=True
        )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db(test_db_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_db_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:

        yield session
        await session.rollback()

@pytest.fixture  # Add the test_client fixture here
def test_client():
    with TestClient(app) as client:
        yield client