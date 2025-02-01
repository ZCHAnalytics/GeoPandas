# 🚄 lifespan.py - FastAPI Train Delay API

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager 

from db.db_main import engine, get_db
from db.db_schema_alchemy import TrainTracking
from tests.db_schema_pydantic import TrainCreate # Pydantic schema for validation
from services.trains_delays import get_delays_info
from services.trains_plots import plot_delays_trends

# Default station codes (Finsbury Park → Kings Cross)
DEFAULT_ORIGIN = "FPK" 
DEFAULT_DESTINATION = "KGX"  

# 1. OPTIONAL -- Fetch and Store train data only once at the startup of the FastAPI app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan event handler to pre-fetch and store train data at startup.
    """
    async with AsyncSession(engine) as db:
        await fetch_and_store_past_trains(DEFAULT_ORIGIN, DEFAULT_DESTINATION, db)
    yield

# Instantiate FastAPI app with lifespan startup task
app = FastAPI(lifespan=lifespan)

# 2. Get train data and save it in the database 

async def fetch_and_store_past_trains(origin: str, destination: str, db: AsyncSession):
    """
    Call function get_delays_info() to retrieve train delays as a Pandas DataFrame.
    
    Args:
        origin (str): Origin station code.
        destination (str): Destination station code.
        db (AsyncSession): Async database session.
    
    Returns:
        dict: Message indicating the number of stored train records.
    """
        
    df = get_delays_info(origin, destination)
    if df.empty: # To prevent unnecessary db operations
        print("No train data found. Skipping db update")
        return {"message": "No train data found"}
    
    print(df.head()) # Print first five rows of the returned DataFrame to the consoel for validation

    # Format records from JSON to list of dictionaires 
    all_trains = [] # Initialise an empty list for storing dictionaries 
    for train in df.to_dict(orient="records"): # convert a Pandas DataFrame into a list of dictionaires (one dictrionary per row)
        
        all_trains.append(TrainTracking(**train)) # Creates `TrainTracking` object for each record
    
    # Add records to db
    db.add_all(all_trains) # Adds all train records to the session 
    await db.commit() # Saves changes in the database 
    """
    Alternative - replace for-loop with list comprehension and `async with db` for closing the database session after use:

    # Format records from JSON using list comprehension 
    all_trains = [TrainTracking(**train) for train in df.to_dict(orient="records")]

    async with db:
        db.add_all(all_trains)
        await db.commit()
    """

    return {"message": f"Stored {len(all_trains)} train records in DB"}

# 4. Endpoint, call get_delays_info() function to return train data  
@app.get("/api/delays")

def fetch_delays_info(origin:str = DEFAULT_ORIGIN, destination: str = DEFAULT_DESTINATION):
    """
    Retrieve train delay information for a given route.

    Args:
        origin (str): Origin station code.
        destination (str): Destination station code.

    Returns:
        list: List of train delay records as dictionaries.
    """
    df = get_delays_info(origin, destination)
    return df.to_dict(orient="records")


# get all train records
@app.get("/api/trains/")
async def get_trains(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all train records from the database.

    Args:
        db (AsyncSession): Async database session.

    Returns:
        list: List of train records.
    """
    result = await db.execute(select(TrainTracking))
    return result.scalars().all()

