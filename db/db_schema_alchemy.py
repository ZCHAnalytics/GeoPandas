# db_schema.py - SQLAlchemy Database Schema

from sqlalchemy import Column, Integer, String, Date, Time, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TrainTracking(Base):
    """
    SQLAlchemy model for storing train tracking data.
    """
    __tablename__ = "arrivals_tracking"

    id = Column(Integer, primary_key=True)
    run_date = Column(Date, nullable=False)
    service_id = Column(String(10), nullable=False)
    operator = Column(String(50), nullable=False)
    origin = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    scheduled_arrival = Column(Time, nullable=False)
    actual_arrival = Column(Time, nullable=True)
    is_actual = Column(Boolean, nullable=True)  
    delay_minutes = Column(Integer, nullable=True)

    # ✅ New fields
    is_passenger_train = Column(Boolean, nullable=False, default=True)  # True if passenger train
    next_day_arrival = Column(Boolean, nullable=False, default=False)  # True if arrival is after midnight
    was_scheduled_to_stop = Column(Boolean, nullable=False, default=True)  # True if originally scheduled to stop
    stop_status = Column(String(20), nullable=False, default="UNKNOWN")  # Display status

