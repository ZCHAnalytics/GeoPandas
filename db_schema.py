# db_schema.py

from sqlalchemy import Column, Integer, String, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base() # each schema follows the base template

# Convert time strings to datetime format 
def convert_to_time(value):
    try:
        return datetime.strptime(value, "%H%M").time() if value else None
    except (ValueError, TypeError):
        return None  # Return None if conversion fails

# SQLAlchemy Database 
class TrainTracking(Base): # Define the db table 
    __tablename__ = "train_tracking"

    #Define table columns and constraints
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), nullable=False)
    operator = Column(String(50), nullable=False)
    origin = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    scheduled_arrival = Column(Time, nullable=False)
    actual_arrival = Column(Time, nullable=False)
    delay_minutes = Column(Integer, nullable=True)
    date = Column(Date, nullable=False) 
    
    def __init__(self, **kwargs):
        # Convert times strings
        if "scheduled_arrival" in kwargs:
            kwargs["scheduled_arrival"]= convert_to_time(kwargs["scheduled_arrival"])
        if "actual_arrival" in kwargs:
            kwargs["actual_arrival"] = convert_to_time(kwargs["actual_arrival"])
        super().__init__(**kwargs)
        