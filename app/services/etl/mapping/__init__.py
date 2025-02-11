# app/services/etl/mapping/__init__.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import setup_logging
from .data_fetcher import fetch_delay_data
from .map_generator import generate_map

logger = setup_logging()

async def generate_html_map(db: AsyncSession, hours: int = 1) -> Optional[str]:
    """Generate HTML map showing train delays."""
    try:
        # Fetch data
        delay_data = await fetch_delay_data(db, hours)
        
        # Generate map
        map_generator = generate_map()
        return map_generator.generate(delay_data)
        
    except Exception as e:
        logger.error("❌ Failed to generate map: %s", str(e))
        return None

__all__ = ['generate_html_map']