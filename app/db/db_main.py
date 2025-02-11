# app/db/db_main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import event
# Project modules
from app.core.config import settings
from app.core.logging_config import configure_logging

logger = configure_logging()

class AsyncDatabaseManager:
    """
    Manages database connections and session creation.
    
    Attributes:
        engine: AsyncEngine instance for database connections
        SessionLocal: Async session factory
    """
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._async_session_factory: Optional[sessionmaker] = None        
        
    @property
    def engine(self) -> AsyncEngine:
        """
        Gets or creates the database engine.
        
        Returns:
            AsyncEngine: SQLAlchemy async engine instance
        
        Raises:
            RuntimeError: If database URL is not configured
        """
        if not self._engine:
            if not settings.database_url:
                raise RuntimeError("Database URL is not configured")
            
            #Convert PostgresDSN to string
            database_url = str(settings.database_url)
            self._engine = create_async_engine(
                database_url, # use the string version 
                pool_pre_ping=True,  # Enable connection health checks
                pool_size=settings.db_pool_size,  # From settings
                max_overflow=settings.db_max_overflow,  # From settings
                echo=settings.db_echo_log,  # From settings
                pool_recycle=settings.db_pool_recycle,  # From settings
            )
            
            # Add engine event listeners
            event.listen(self._engine.sync_engine, 'connect', self._on_connect)
            event.listen(self._engine.sync_engine, 'checkout', self._on_checkout)
            
            logger.info("✅ Database engine created successfully")
            
        return self._engine
    
    @property
    def async_session_factory(self) -> sessionmaker:
        """
        Gets or creates the session factory.
        
        Returns:
            sessionmaker: SQLAlchemy session factory
        """
        if not self._async_session_factory:
            self._async_session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._async_session_factory
    
    async def close(self) -> None:
        """Closes the database engine and cleans up resources."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._async_session_factory = None
            logger.info("✅ Database connection closed")
    
    @staticmethod
    def _on_connect(dbapi_connection, connection_record):
        """Callback for new database connections."""
        logger.debug("🔌 New database connection established")
        
        # Set session parameters synchronously
        cursor = dbapi_connection.cursor()
        cursor.execute("SET timezone='UTC';")
        cursor.close()
    
    @staticmethod
    def _on_checkout(dbapi_connection, connection_record, connection_proxy):
        """Callback for connection checkout from pool."""
        logger.debug("🔄 Database connection checked out from pool")

# Create global database manager instance
db_manager = AsyncDatabaseManager()

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Yields:
        AsyncSession: Database session
    
    Raises:
        SQLAlchemyError: If database operations fail
    """
    session = db_manager.async_session_factory()
    
    try:
        logger.debug("🎯 New database session created")
        yield session
        await session.commit() 
    except SQLAlchemyError as e:
        logger.error("❌ Database session error: %s", str(e))
        await session.rollback()
        raise
    finally:
        await session.close()
        logger.debug("🎯 Database session closed")

async def close_database_connections() -> None:
    """Closes database connections."""
    await db_manager.close()