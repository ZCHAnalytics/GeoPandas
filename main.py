# 🚄 main.py - FastAPI Train Delay API (bulk operations only)

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_main import get_db
from db.db_schema_alchemy import TrainTracking
from services.trains_delays import get_delays_info
from services.trains_plots import router as plots_router # Import router for visualisation 

# Default station codes (Finsbury Park → Kings Cross)
DEFAULT_ORIGIN = "FPK" 
DEFAULT_DESTINATION = "KGX"  

# 1. Get train data and save it in the database 

async def fetch_and_store_past_trains(origin: str, destination: str, db: AsyncSession):
    """
    Call function get_delays_info() to retrieve train delays as a Pandas DataFrame.
    """
        
    df = get_delays_info(origin, destination)
    if df.empty: # To prevent unnecessary db operations
        print("No train data found. Skipping db update")
        return {"message": "No train data found"}
    
    print(df.head()) # Print first five rows of the returned DataFrame to the consoel for validation

    # Format records from JSON using list comprehension 
    all_trains = [TrainTracking(**train) for train in df.to_dict(orient="records")]

    async with db:
        db.add_all(all_trains)
        await db.commit()

    return {"message": f"Stored {len(all_trains)} train records in DB"}

# Initialise FastAPI app
app = FastAPI()
app.include_router(plots_router) # Register the router plots services.plots


# 2. Endpoint to return train data  

@app.get("/api/delays")

def fetch_delays_info(origin:str = DEFAULT_ORIGIN, destination: str = DEFAULT_DESTINATION):
    """
    Retrieve train delay information for a given route.
    """
    df = get_delays_info(origin, destination)
    return df.to_dict(orient="records")

 
# 3. Function to refresh train data in the database 

@app.post("/api/update_delays/")
async def update_delays(db: AsyncSession = Depends(get_db)):
    """
    Fetch and store past 6 days of train delays in the database.
    """
    return await fetch_and_store_past_trains(DEFAULT_ORIGIN, DEFAULT_DESTINATION, db)
