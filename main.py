# FastAPI Train API + Data Pipeline (Extract → Clean → Upload)
import logging 
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Project modules for the data pipeline
from data_pipeline.extract import extract_data
from data_pipeline.clean import process_data
from data_pipeline.merge import merge_geospatial_data
from data_pipeline.utils import upload_to_db
from data_pipeline.map import generate_html_map

# Set up logging 
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
    logger.info("🚀 Extracting live data for station %s over the past %d days...", STATION, DAYS)
    raw_data = extract_data(STATION, DAYS)
    
    if not raw_data or "services" not in raw_data:
        logger.error("❌ No valid raw data found. Skipping further processing.")
        yield
        return  # Stop execution if no data
    
    # ✅ 2 Step 2:  Process & clean extracted data    
    logger.info("Starting processing and cleaning of extracted data...")
    df_clean = process_data(raw_data)
    
    if df_clean.empty:
        logger.error("❌ No valid train records after processing. Skipping upload.")
        yield
        return  # Stop execution if no clean data
    
    # ✅ Step 3: Merge with geospatial data 
    logger.info("🚀 Merging geospatial data with cleaned train records...")
    df_merged = merge_geospatial_data(df_clean)
    if df_merged.empty:
        logger.error("❌ No valid train records after merging geospatial data.")
        yield
        return
     
    # ✅ Step 4: Upload cleaned data to PostgreSQL
    logger.info("🚀 Running database upload for %d records...", len(df_merged))
    await upload_to_db(df_merged)
    
    # ✅ Step 5: Generate HTML Map showing delays
    logger.info("🚀 Generating train delay map...")
    map_path = generate_html_map(df_merged)
    logger.info("✅ Map Saved to %s", map_path)

    logger.info("✅ Data pipeline completed successfully!")
    yield  # ✅ Allows API to start after setup

# ✅ Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


"""
# ✅ Example FastAPI endpoints for monitoring purposes
@app.get("/")
def home():
    return {"message": "Train Delay API is running!"}

# TODO: Example dynamic API endpoint using parameters
@app.get("/api/station/{station}/date/{date}")
def get_trains(station: str, date: str):
    
    Example API endpoint to retrieve train data for a specific station and date.
    
    raw_data = extract_data(station, date)
    return raw_data if raw_data else {"error": "No data found"}

    """
# ✅ Run FastAPI server (if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)