# SQLAlchemy Database Schema

from sqlalchemy import Column, Integer, String, Date, Time, Float, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TrainTracking(Base):
    """
    SQLAlchemy model for storing train tracking data.
    """
    __tablename__ = "arrivals_tracking"

    id = Column(Integer, primary_key=True)

    # Date fields
    run_date = Column(Date, nullable=False)

    # Train identification
    service_id = Column(String(10), nullable=False)
    operator = Column(String(50), nullable=False)

    # ✅ New geospatial fields
    origin = Column(String(50), nullable=False)
    origin_crs = Column(String(6), nullable=True)
    origin_latitude = Column(Float, nullable=True)
    origin_longitude = Column(Float, nullable=True)
    
    destination = Column(String(50), nullable=False)
    destination_crs = Column(String(6), nullable=True)
    destination_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)

    scheduled_arrival = Column(Time, nullable=False)
    actual_arrival = Column(Time, nullable=True)
    is_actual = Column(Boolean, nullable=True)  
    delay_minutes = Column(Integer, nullable=True)

    # ✅ New fields
    is_passenger_train = Column(Boolean, nullable=False, default=True)  # True if passenger train
    was_scheduled_to_stop = Column(Boolean, nullable=False, default=True)  # True if originally scheduled to stop
    stop_status = Column(String(20), nullable=False, default="UNKNOWN")  # Display status

