# schema.py 

from pydantic import BaseModel
from datetime import time, date 

class TrainCreate(BaseModel):
    train_number: str
    operator: str
    origin: str
    destination: str
    scheduled_arrival: time
    actual_arrival: time
    delay_minutes: int
    date: date 
