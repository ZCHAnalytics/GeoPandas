# app/models/db_models.py

from typing import Optional
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, Float, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from pydantic import BaseModel

from app.core.logging_config import configure_logging

logger = configure_logging()

Base = declarative_base()

class TrainTracking(Base):
    """
    SQLAlchemy model for storing train tracking data with PostGIS integration.
    
    Attributes:
        id (int): Primary key
        run_date (date): Date of the train service
        service_id (str): Unique identifier for the train service
        operator (str): Train operating company
        origin (str): Origin station name
        origin_crs (str): Origin station CRS code
        origin_latitude (float): Origin station latitude
        origin_longitude (float): Origin station longitude
        origin_geom (Geometry): PostGIS geometry for origin location
        destination (str): Destination station name
        destination_crs (str): Destination station CRS code
        destination_latitude (float): Destination station latitude
        destination_longitude (float): Destination station longitude
        destination_geom (Geometry): PostGIS geometry for destination location
        scheduled_arrival (time): Scheduled arrival time
        actual_arrival (time): Actual arrival time
        is_actual (bool): Whether the arrival time is actual or estimated
        delay_minutes (int): Delay in minutes
        is_passenger_train (bool): Whether the train carries passengers
        was_scheduled_to_stop (bool): Whether the train was scheduled to stop
        stop_status (str): Current stop status
    """
    __tablename__ = "arrivals_tracking"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Date fields
    run_date = Column(Date, nullable=False, index=True) # for historical analysis
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

    # Train identification
    service_id = Column(String(10), nullable=False, index=True)
    operator = Column(String(50), nullable=False, index=True)

    # Origin details with PostGIS integration
    origin = Column(String(50), nullable=False)
    origin_crs = Column(String(6))
    origin_latitude = Column(Float)
    origin_longitude = Column(Float)
    origin_geom = Column(Geometry('POINT', srid=4326))
    
    # Destination details with PostGIS integration
    destination = Column(String(50), nullable=False)
    destination_crs = Column(String(6))
    destination_latitude = Column(Float)
    destination_longitude = Column(Float)
    destination_geom = Column(Geometry('POINT', srid=4326))

    # Timing information
    scheduled_arrival = Column(TIMESTAMP, nullable=False)
    actual_arrival = Column(TIMESTAMP)
    is_actual = Column(Boolean, default=False)
    delay_minutes = Column(Integer)

    # Additional train information
    is_passenger_train = Column(Boolean, nullable=False, default=True)
    was_scheduled_to_stop = Column(Boolean, nullable=False, default=True)
    stop_status = Column(String(20), nullable=False, default="UNKNOWN")

    def __repr__(self) -> str:
        """String representation of the train tracking record."""
        return (
            f"TrainTracking(service_id={self.service_id}, "
            f"run_date={self.run_date}, "
            f"origin={self.origin}, "
            f"destination={self.destination}, "
            f"delay_minutes={self.delay_minutes})"
        )


# Pydantic model for API responses and validation
class TrainTrackingSchema(BaseModel):
    """
    Pydantic model for train tracking data validation and serialization.
    """
    id: Optional[int]
    run_date: datetime 
    service_id: str
    operator: str
    origin: str
    origin_crs: Optional[str]
    origin_latitude: Optional[float]
    origin_longitude: Optional[float]
    destination: str
    destination_crs: Optional[str]
    destination_latitude: Optional[float]
    destination_longitude: Optional[float]
    scheduled_arrival: datetime
    actual_arrival: Optional[datetime]
    is_actual: bool = False
    delay_minutes: Optional[int]
    is_passenger_train: bool = True
    was_scheduled_to_stop: bool = True
    stop_status: str = "UNKNOWN"

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# Database indices configuration
indices = [
    ('idx_train_tracking_run_date', 'arrivals_tracking', ['run_date']),
    ('idx_train_tracking_service_id', 'arrivals_tracking', ['service_id']),
    ('idx_train_tracking_operator', 'arrivals_tracking', ['operator']),
    ('idx_train_tracking_origin_geom', 'arrivals_tracking', ['origin_geom'], 'gist'),
    ('idx_train_tracking_destination_geom', 'arrivals_tracking', ['destination_geom'], 'gist'),
]

# Create PostGIS extension and indices
def setup_postgis(engine):
    """
    Sets up PostGIS extension and creates necessary indices.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    try:
        with engine.connect() as conn:
            conn.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
            
            # Create indices
            for idx_name, table, columns, *method in indices:
                idx_method = method[0] if method else ''
                col_list = ', '.join(columns)
                idx_sql = f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table} USING {idx_method} ({col_list});'
                conn.execute(idx_sql)
                
        logger.info("✅ PostGIS extension and indices successfully configured")
    except Exception as e:
        logger.error("❌ Error setting up PostGIS: %s", str(e))
        raise