# db_init.py - Initialize Database with SQLAlchemy

import asyncio
from db_main import engine
from db_schema_alchemy import Base
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

async def init_db():
    """
    Initialize the database:
    - (Optional) Drops all existing tables to start fresh.
    - Creates tables based on the SQLAlchemy schema.
    """
    try: 

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)  # Clears existing tables
            await conn.run_sync(Base.metadata.create_all)  # Creates new tables if they don't exist 
        logger.info("✅ Database and tables created!")
    except Exception as e:
        logger.error("Failed to initialised the datbase: %s", e)
        
# Run db initialisation when the script is executed 
if __name__ == "__main__":
    # Fix event loop policy for Windows compatability 
    if asyncio.get_event_loop_policy().__class__.__name__ == "WindowsProactorEventLoopPolicy":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(init_db())