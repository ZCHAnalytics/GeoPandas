# main.py - FastAPI Train API + Data Pipeline (Extract → Clean → Upload)

import logging # v3 addition
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Project modules
from data_pipeline.extract import extract_data
from data_pipeline.clean import process_data
from data_pipeline.utils import upload_to_db

# Set up logging v3
logger = logging.getLogger("train_api")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ✅ Default station & date
STATION = "FPK"  # Finsbury Park (arrivals)
DAYS = 7

# ✅ Lifespan function to run data pipeline before FastAPI starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Running data pipeline before starting API...")
    
    # ✅ Step 1 : Extract live data 
    raw_data = extract_data(STATION, DAYS)
    if not raw_data or "services" not in raw_data:
        logger.error("❌ No valid raw data found. Skipping further processing.")
        yield
        return  # Stop execution if no data
    
    # ✅ 2 Step 2:  Process & clean extracted data    
    df_clean = process_data(raw_data)
    if df_clean.empty:
        logger.error("❌ No valid train records after processing. Skipping upload.")
        yield
        return  # Stop execution if no clean data
    
    # ✅ Step 3: Upload cleaned data to PostgreSQL
    logger.info("🚀 Running database upload for %d records...", len(df_clean))
    await upload_to_db(df_clean)
    
    logger.info("✅ Data pipeline completed!")
    yield  # ✅ Allows API to start after setup

# ✅ Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

"""
# ✅ Example FastAPI endpoints for monitoring purposes
@app.get("/")
def home():
    return {"message": "Train Delay API is running!"}

# TODO - use of dynamic parameters
@app.get("/api/station/{station}/date/{date}")
def get_trains(station: str, date: str):

    Example API endpoint to retrieve train data (to be modified).

    raw_data = extract_data(STATION, DAYS)
    return raw_data if raw_data else {"error": "No data found"}

    """
# ✅ Run FastAPI server (if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
