# app/services/etl/extract.py
import os 
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.logging_config import configure_logging
from app.services.trains_main import get_train_arrivals

logger = configure_logging()

# Define output directory using settings
OUTPUT_DIR = os.path.join("data", "outputs", "raw_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def extract_data_for_date(station: str, date: str) -> Optional[Dict[str, Any]]:
    """
    Extract raw train data for a specific date.
    
    Args:
        station (str): Station code (e.g., "FPK" for Finsbury Park)
        date (str): Specific date to fetch data for
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing extracted train services or None if error.
    """

    raw_data = await get_train_arrivals(station, date)  
    
    if raw_data and "services" in raw_data:
        return raw_data
    else:
        logger.error("❌ No valid train data found for %s on %s", station, date)
        return None


async def extract_and_save_arrivals_data(station: str, days: int = 7) -> Dict[str, Any]:
    """
    Extract raw train data and save locally.
    
    Args:
        station (str): Station code (e.g., "FPK" for Finsbury Park)
        days (int): Number of past days to extract (default: 7)
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted train services
    """
    arrivals_data = {"services": []}  # Initialise empty container

    for i in range(days):
        # Calculate the date string for 'i' days ago
        date = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") # Ensure date is a string
        
        raw_data = await extract_data_for_date(station, date)
    
        if raw_data:
            # Append to full dataset
            arrivals_data["services"].extend(raw_data["services"])
        else: 
            logger.error("❌ No valid train data found for %s on %s", station, str(date))
            
    
    return arrivals_data