# db_schema_alchemy.py - SQLAlchemy Database Schema

from sqlalchemy import Column, Integer, String, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base() # each schema follows the base template

# Function to convert time strings to datetime.time format 
def convert_to_time(value):
    """
    Convert time string (HHMM) to a datetime.time object.
    Returns None if fails.
    """

    try:
        return datetime.strptime(value, "%H%M").time() if value else None
    except (ValueError, TypeError) as e:
        print(f"Time conversion error: {e}") # Error logging
        return None

# Define TrainTracking table schema: 
class TrainTracking(Base): # Define the db table 
    """
    SQLAlchemy model for storing train tracking data.
    """
    __tablename__ = "train_tracking"

    #Define table columns and constraints
    id = Column(Integer, primary_key=True)
    train_number = Column(String(10), nullable=False)
    operator = Column(String(50), nullable=False)
    origin = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    scheduled_arrival = Column(Time, nullable=False)
    actual_arrival = Column(Time, nullable=False)
    delay_minutes = Column(Integer, nullable=True)
    date = Column(Date, nullable=False) 
    
    def __init__(self, **kwargs):
        """
        Initialize TrainTracking instance. Arguments are passed as a dictionary `kwargs`
        Automatically converts time strings to datetime.time format.
        """            
        if "scheduled_arrival" in kwargs:
            kwargs["scheduled_arrival"]= convert_to_time(kwargs["scheduled_arrival"])
        if "actual_arrival" in kwargs:
            kwargs["actual_arrival"] = convert_to_time(kwargs["actual_arrival"])
        super().__init__(**kwargs) # passes the modified kwargs dictionary to SQLALchemy Base class
        