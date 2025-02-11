# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, ConfigDict
from typing import Optional
 
class Settings(BaseSettings):
    """
    Application settings.

    Database settings:
        database_url: Connection string for the database.
        db_pool_size: The size of the database connection pool.
        db_max_overflow: The maximum number of connections to allow in the pool.
        db_echo_log: Whether to enable SQL query logging.
        db_pool_recycle: The number of seconds after which inactive connections are recycled.

    Test database settings:
        test_database_url: Connection string for the test database.

    Database admin credentials (for test setup):
        db_admin_user: Username for the database administrator.
        db_admin_password: Password for the database administrator.

    Database initialisation settings:
        db_drop_existing: Whether to drop existing tables before initialisation.
        db_enable_migration: Whether to enable database migrations.
        db_verify_setup: Whether to verify the database setup after initialisation.

    PostGIS settings:
        postgis_srid: The SRID (Spatial Reference System Identifier) to use for PostGIS.

    Data extraction settings:
        station: The default station code for data extraction.
        days: The default number of days to extract data for.

    Environment variables:
        RTT_USERNAME: Username for the Real Time Trains API.
        RTT_PASSWORD: Password for the Real Time Trains API.
        RTT_ENDPOINT: Endpoint URL for the Real Time Trains API.
    """

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Database settings
    database_url: PostgresDsn
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo_log: bool = False
    db_pool_recycle: int = 3600 

    # Test database settings
    test_database_url: PostgresDsn

    # Database admin credentials (for test setup)
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None

    # Database initialisation settings
    db_drop_existing: bool = True
    db_enable_migration: bool = True
    db_verify_setup: bool = True

    # PostGIS settings
    postgis_srid: int = 4326 
    station: str = "FPK"  # Default 
    days: int = 7

    # Environment variables 
    RTT_USERNAME: str 
    RTT_PASSWORD: str 
    RTT_ENDPOINT: str 

  

    # Derived configuration
    @property 
    def base_url(self) -> str:
        return f"https://{self.RTT_ENDPOINT}/json/search"

# Initialise settings
settings = Settings()
