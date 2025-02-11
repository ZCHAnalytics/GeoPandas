# app/db/db_init.py
import asyncio
from typing import Optional
import sys
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import text
from alembic.config import Config
from alembic import command

from app.db.db_main import engine
from app.models.db_models import Base
from app.core.logging_config import setup_logging
from app.core.config import settings

logger = setup_logging()

class AsyncDatabaseInitialiser:
    """Handles database initialisation and schema management."""
    
    def __init__(self):
        self.engine = engine
    
    async def _enable_postgis_extensions(self, connection: AsyncConnection) -> None:
        """
        Enables PostGIS extension in the database.
        
        Args:
            connection: Active database connection
        """
        try:
            # Enable PostGIS
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            # Enable additional PostGIS extensions if needed
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
            logger.info("✅ PostGIS extensions enabled successfully")
        except Exception as e:
            logger.error("❌ Failed to enable PostGIS: %s", str(e))
            raise

    async def _create_geometry_indices(self, connection: AsyncConnection) -> None:
        """
        Creates spatial indices for geometry columns.
        
        Args:
            connection: Active database connection
        """
        try:
            # Create spatial indices for your geometry columns
            await connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_origin_geom 
                ON arrivals_tracking USING GIST (origin_geom);
            """))
            
            await connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_destination_geom 
                ON arrivals_tracking USING GIST (destination_geom);
            """))
            
            logger.info("✅ Spatial indices created successfully")
        except Exception as e:
            logger.error("❌ Failed to create spatial indices: %s", str(e))
            raise

    async def _create_geometry_update_triggers(self, connection: AsyncConnection) -> None:
        """
        Sets up custom database functions and triggers.
        
        Args:
            connection: Active database connection
        """
        try:
            # Example: Create a function to automatically update geometry columns
            await connection.execute(text("""
                CREATE OR REPLACE FUNCTION update_geom_columns()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.origin_geom = ST_SetSRID(
                        ST_MakePoint(NEW.origin_longitude, NEW.origin_latitude),
                        4326
                    );
                    NEW.destination_geom = ST_SetSRID(
                        ST_MakePoint(NEW.destination_longitude, NEW.destination_latitude),
                        4326
                    );
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            # Create trigger
            await connection.execute(text("""
                DROP TRIGGER IF EXISTS update_geom_trigger ON arrivals_tracking;
                CREATE TRIGGER update_geom_trigger
                BEFORE INSERT OR UPDATE ON arrivals_tracking
                FOR EACH ROW
                EXECUTE FUNCTION update_geom_columns();
            """))
            
            logger.info("✅ Database functions and triggers created successfully")
        except Exception as e:
            logger.error("❌ Failed to setup database functions: %s", str(e))
            raise

    def _run_migrations(self) -> None:
        """
        Runs database migrations using Alembic.
        """
        try:
            # Configure Alembic
            alembic_cfg = Config("alembic.ini")
            
            # Run migrations
            command.upgrade(alembic_cfg, "head")
            logger.info("✅ Database migrations completed successfully")
        except Exception as e:
            logger.error("❌ Failed to run migrations: %s", str(e))
            raise

    async def initialise_database(self, drop_existing: bool = False) -> None:
        """
        Initializes the database with complete setup.
        
        Args:
            drop_existing: If True, drops existing tables before creation
        """
        try:
            async with engine.begin() as conn:
                if drop_existing:
                    logger.warning("⚠️ Dropping existing tables...")
                    await conn.run_sync(Base.metadata.drop_all)
                
                # Create tables
                await conn.run_sync(Base.metadata.create_all)
                
                # Enable PostGIS
                await self._enable_postgis_extensions(conn)
                
                # Create spatial indices
                await self._create_geometry_indices(conn)
                
                # Setup functions and triggers
                await self._create_geometry_update_triggers(conn)
                
            # Run migrations
            self._run_migrations()
            
            logger.info("✅ Database initialization completed successfully!")
            
        except Exception as e:
            logger.error("❌ Database initialization failed: %s", str(e))
            raise

    async def verify_database_setup(self) -> bool:
        """
        Verifies database setup and connectivity.
        
        Returns:
            bool: True if verification passes
        """
        try:
            async with engine.connect() as conn:
                # Check PostGIS
                result = await conn.execute(text("SELECT PostGIS_Version();"))
                postgis_version = result.scalar()
                logger.info("✅ PostGIS version: %s", postgis_version)
                
                # Check spatial indices
                result = await conn.execute(text("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = 'arrivals_tracking' 
                    AND indexname LIKE 'idx_%_geom';
                """))
                indices = result.fetchall()
                logger.info("✅ Found %d spatial indices", len(indices))
                
                # Check triggers
                result = await conn.execute(text("""
                    SELECT tgname 
                    FROM pg_trigger 
                    WHERE tgrelid = 'arrivals_tracking'::regclass;
                """))
                triggers = result.fetchall()
                logger.info("✅ Found %d triggers", len(triggers))
                
                return True
        except Exception as e:
            logger.error("❌ Database verification failed: %s", str(e))
            return False

async def initialise_database(drop_existing: bool = False) -> None:
    """
    Main function to initialise the database.
    
    Args:
        drop_existing: If True, drops existing tables before creation
    """
    initialiser = AsyncDatabaseInitialiser()
    
    try:
        await initialiser.init_db(drop_existing)
        
        # Verify setup
        if await initialiser.verify_database():
            logger.info("✅ Database setup verified successfully")
        else:
            logger.warning("⚠️ Database setup verification failed")
            
    except Exception as e:
        logger.error("❌ Database initialisation failed: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    # Fix event loop policy for Windows compatibility
    if sys.platform == "win32":
        try:
            from asyncio import WindowsSelectorEventLoopPolicy
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        except Exception as e:
            logger.error("❌ Failed to set Windows event loop policy: %s", str(e))
    
    # Run initialisation
    asyncio.run(initialise_database(drop_existing=settings.db_drop_existing))