# app/services/etl/clean.py
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Any
import pandas as pd
from pydantic import BaseModel
# Project modules
from app.core.logging_config import configure_logging
from app.core.config import settings

logger = configure_logging()
# Define output directory using settings

OUTPUT_DIR = os.path.join("data", "outputs", "cleaned_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TrainService(BaseModel):
    """Pydantic model for validating train service data."""
    run_date: str
    service_id: str
    operator: str
    scheduled_arrival: str
    actual_arrival: Optional[str]
    is_actual: bool = False
    is_passenger_train: bool = True
    origin: str = "UNKNOWN"
    destination: str = "UNKNOWN"
    was_scheduled_to_stop: bool = False
    stop_status: str = "UNKNOWN"

    class Config:
        arbitrary_types_allowed = True

def convert_time_string(time_str: str, run_date: datetime.date) -> Optional[datetime]:
    """
    Converts HHMM time string to datetime object.
    
    Args:
        time_str (str): Time in HHMM format
        run_date (datetime.date): The date to combine with the time
        
    Returns:
        Optional[datetime]: Datetime object or None if conversion fails
    """
    try:
        time_obj = datetime.strptime(time_str, "%H%M").time()
        return datetime.combine(run_date, time_obj)
    except ValueError as e:
        logger.error("❌ Invalid time format: %s - %s", time_str, str(e))
        return None

def calculate_delay(scheduled_dt: datetime, actual_dt: datetime) -> int:
    """
    Calculates delay in minutes between scheduled and actual times.
    
    Args:
        scheduled_dt (datetime): Scheduled arrival datetime
        actual_dt (datetime): Actual arrival datetime
        
    Returns:
        int: Delay in minutes
    """
    delay_delta = actual_dt - scheduled_dt
    return int(delay_delta.total_seconds() // 60)

def process_service(service: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Processes a single train service record.
    
    Args:
        service (Dict[str, Any]): Raw service data
        
    Returns:
        Optional[Dict[str, Any]]: Cleaned service data or None if invalid
    """
    try:
        # Validate service data using Pydantic model
        validated_service = TrainService(**service)
        
        # Parse run date
        run_date = datetime.strptime(validated_service.run_date, "%Y-%m-%d").date()
        
        # Skip if actual arrival is missing
        if not validated_service.actual_arrival:
            return None
            
        # Convert time strings to datetime objects
        scheduled_dt = convert_time_string(validated_service.scheduled_arrival, run_date)
        actual_dt = convert_time_string(validated_service.actual_arrival, run_date)
        
        if not (scheduled_dt and actual_dt):
            return None
            
        # Handle midnight crossing
        if actual_dt.time().hour < 5 and scheduled_dt.time().hour > 20:
            actual_dt = datetime.combine(run_date + timedelta(days=1), actual_dt.time())
            
        # Calculate delay
        delay_minutes = calculate_delay(scheduled_dt, actual_dt)
        
        # Return cleaned record
        return {
            "run_date": run_date,
            "service_id": validated_service.service_id,
            "operator": validated_service.operator,
            "is_passenger_train": validated_service.is_passenger_train,
            "scheduled_arrival": scheduled_dt.strftime("%H:%M"),
            "actual_arrival": actual_dt.strftime("%H:%M"),
            "is_actual": validated_service.is_actual,
            "origin": validated_service.origin,
            "destination": validated_service.destination,
            "was_scheduled_to_stop": validated_service.was_scheduled_to_stop,
            "stop_status": validated_service.stop_status,
            "delay_minutes": delay_minutes
        }
        
    except Exception as e:
        logger.error("❌ Error processing service: %s - %s", service.get("service_id", "UNKNOWN"), str(e))
        return None

def process_data(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Process and clean extracted train arrival data.
    
    Args:
        raw_data (Dict[str, Any]): JSON data extracted from API
        
    Returns:
        pd.DataFrame: Cleaned train arrival data
    """
    logger.info("🚀 Starting data cleaning process...")
    
    cleaned_delays: List[Dict[str, Any]] = []
    missing_actual_arrival: List[Dict[str, Any]] = []
    
    total_services = len(raw_data.get("services", []))
    logger.info("📊 Processing %d train services...", total_services)
    
    for service in raw_data.get("services", []):
        cleaned_service = process_service(service)
        
        if cleaned_service:
            cleaned_delays.append(cleaned_service)
        else:
            # Store services with missing actual arrival
            try:
                missing_actual_arrival.append({
                    "run_date": service.get("run_date"),
                    "service_id": service.get("service_id"),
                    "operator": service.get("operator"),
                    "scheduled_arrival": service.get("scheduled_arrival"),
                    "origin": service.get("origin", "UNKNOWN"),
                    "destination": service.get("destination", "UNKNOWN")
                })
            except Exception as e:
                logger.error("❌ Error storing missing arrival record: %s", str(e))
    
    # Create DataFrames and save to files
    try:
        if cleaned_delays:
            df_cleaned = pd.DataFrame(cleaned_delays)
            cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_delays_data.csv")
            df_cleaned.to_csv(cleaned_path, index=False)
            logger.info("✅ Saved %d cleaned records to %s", len(cleaned_delays), cleaned_path)
        else:
            logger.warning("⚠️ No valid records found for cleaning")
            df_cleaned = pd.DataFrame()
            
        if missing_actual_arrival:
            df_missing = pd.DataFrame(missing_actual_arrival)
            missing_path = os.path.join(OUTPUT_DIR, "missing_actual_arrivals.csv")
            df_missing.to_csv(missing_path, index=False)
            logger.info("ℹ️ Saved %d records with missing arrivals to %s", 
                       len(missing_actual_arrival), missing_path)
            
        # Log summary statistics
        logger.info("📊 Processing Summary:")
        logger.info("   - Total services processed: %d", total_services)
        logger.info("   - Valid records: %d", len(cleaned_delays))
        logger.info("   - Missing arrivals: %d", len(missing_actual_arrival))
        
    except Exception as e:
        logger.error("❌ Error saving processed data: %s", str(e))
        if not cleaned_delays:
            return pd.DataFrame()  # Return empty DataFrame on error
    # To check a specific column:
    print(df_cleaned['run_date'].dtype)
    print(df_cleaned['scheduled_arrival'].dtype)
    print(df_cleaned['actual_arrival'].dtype)
    
    return df_cleaned