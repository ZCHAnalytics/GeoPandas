# main.py - FastAPI Train API + Data Pipeline (Extract → Clean → Upload)

import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from data_pipeline.extract import extract_data
from data_pipeline.clean import process_data
from data_pipeline.utils import upload_to_db
from datetime import datetime

# ✅ Default station & date
STATION = "FPK"  # Finsbury Park (arrivals)
DAYS = 7

# ✅ Lifespan function to run data pipeline before FastAPI starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 Running data pipeline before starting API...")
    raw_data = extract_data(STATION, DAYS)
    if not raw_data or "services" not in raw_data:
        print("❌ No valid raw data found. Skipping further processing.")
        yield
        return  # Stop execution if no data
    
    # ✅ Process & clean extracted data    
    df_clean = process_data(raw_data)
    if df_clean.empty:
        print("❌ No valid train records after processing. Skipping upload.")
        yield
        return  # Stop execution if no clean data
    
    # ✅ Upload to PostgreSQL
    print(f"\n🚀 Running database upload for {len(df_clean)} records...")
    await upload_to_db(df_clean)
    
    print("\n✅ Data pipeline completed!")
    yield  # ✅ Allows API to start after setup

# ✅ Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# ✅ Example FastAPI endpoints
@app.get("/")
def home():
    return {"message": "Train Delay API is running!"}

@app.get("/api/station/{station}/date/{date}")
def get_trains(station: str, date: str):
    """
    Example API endpoint to retrieve train data (to be modified).
    """
    raw_data = extract_data(STATION, DAYS)
    return raw_data if raw_data else {"error": "No data found"}

# ✅ Run FastAPI server (if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
