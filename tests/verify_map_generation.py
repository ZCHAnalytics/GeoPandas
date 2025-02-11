# verify_map_generation.py

import asyncio
import os
from app.db.db_main import db_manager
from app.services.etl.mapping import generate_html_map
from app.core.logging_config import setup_logging

logger = setup_logging()

async def verify_map_generation():
    """Verify map generation works correctly."""
    try:
        async with db_manager.SessionLocal() as session:
            logger.info("Starting verification...")
            
            # Generate map
            result = await generate_html_map(session, hours=24)
            
            # Log results
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result value: {result}")
            
            # Verify result
            assert result is not None, "Result should not be None"
            assert isinstance(result, str), f"Expected string, got {type(result)}"
            assert result.endswith('.html'), "Should end with .html"
            assert os.path.exists(result), "File should exist"
            
            logger.info("✅ Verification successful!")
            
            # Clean up
            if os.path.exists(result):
                os.remove(result)
                logger.info("✅ Cleanup completed")
                
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(verify_map_generation())