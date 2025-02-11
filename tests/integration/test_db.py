# tests/test_db.py

import pytest
from app.db.db_main import get_db
from app.models.db_models import TrainTracking

@pytest.mark.asyncio
async def test_db_connection():
    async for db in get_db():
        result = await db.execute("SELECT 1")
        assert result.scalar() == 1