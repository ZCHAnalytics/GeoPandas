# Process & clean train data

import pandas as pd
from datetime import datetime, timedelta
import os
import logging 

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ✅ Define output directory
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure directory exists

def process_data(raw_data):
    """
    Process and clean extracted train arrival data.
    Args:
        raw_data (dict): JSON data extracted from API.
    Returns:
        pd.DataFrame: Cleaned train arrival data.
    """
    cleaned_delays = []
    missing_actual_arrival = [] # Store records with missing actual_arrival

    logger.info("Starting data cleaning...")

    for service in raw_data.get("services", []):
        # Extract top-level fields:
        run_date_str = service.get("run_date")
        service_id = service.get("service_id")
        operator = service.get("operator")
        is_passenger_train = service.get("is_passenger_train")

        # Ensure run_date is present and correctly formatted
        if run_date_str:
            try:
                run_date = datetime.strptime(run_date_str, "%Y-%m-%d").date()
            except ValueError:
                logging.error("❌ Invalid runDate format: %s", run_date_str)
                continue  # Skip invalid dates
        else:
            logging.error("Missing runDate in service: %s", service)
            continue

        # ✅ Extract core arrival details 
        scheduled_arrival = service.get("scheduled_arrival")
        actual_arrival = service.get("actual_arrival")
        is_actual = service.get("is_actual", False)

        # ✅ Extract origin & destination
        origin = service.get("origin", "UNKNOWN")
        destination = service.get("destination", "UNKNOWN")

        # ✅ Extract additional train metadata
        was_scheduled_to_stop = service.get("was_scheduled_to_stop", False)
        stop_status = service.get("stop_status", "UNKNOWN")

        # ✅ Handle missing actual_arrivals
        if not actual_arrival:
            missing_actual_arrival.append({
                "run_date": run_date,
                "service_id": service_id,
                "operator": operator,
                "is_passenger_train": is_passenger_train,
                "scheduled_arrival": scheduled_arrival,
                "actual_arrival": None,
                "is_actual": is_actual,
                "origin": origin,
                "destination": destination,
                "was_scheduled_to_stop": was_scheduled_to_stop,
                "stop_status": stop_status,
                "delay_minutes": None
            })
            #logging.warning("Missing actual arrival for service %s on %s", service_id, run_date_str)
            continue  # Skip this record for the main cleaned dataset
        
        # ✅ Convert HHMM strings to time objects
        try:
            scheduled_time = datetime.strptime(scheduled_arrival, "%H%M").time()
            actual_time = datetime.strptime(actual_arrival, "%H%M").time()
        except ValueError:
            logger.error("❌ Invalid time format: scheduled '%s', actual '%s'", scheduled_arrival, actual_arrival )
            continue  # Skip invalid time formats

        # ✅ Determine adjusted date if delay crosses midnight  
        if actual_time.hour < 5 and scheduled_time.hour > 20:
            scheduled_dt = datetime.combine(run_date, scheduled_time)
            actual_dt = datetime.combine(run_date + timedelta(days=1), actual_time)
        else:
            scheduled_dt = datetime.combine(run_date, scheduled_time)
            actual_dt = datetime.combine(run_date, actual_time)
            
        # ✅ Calculate delay in minutes
        delay_delta = actual_dt - scheduled_dt
        delay_minutes = int(delay_delta.total_seconds() // 60)

        # ✅ Append cleaned data
        cleaned_delays.append({
            "run_date": run_date, 
            "service_id": service_id,
            "operator": operator,
            "is_passenger_train": is_passenger_train,
            "scheduled_arrival": scheduled_time.strftime("%H:%M"),
            "actual_arrival": actual_time.strftime("%H:%M"),
            "is_actual": is_actual,
            "origin": origin,
            "destination": destination,
            "was_scheduled_to_stop": was_scheduled_to_stop,
            "stop_status": stop_status,
            "delay_minutes": int(delay_minutes)
        })
    
    # ✅ Save cleaned delays data if available
    if cleaned_delays:  # Check if list is not empty
        logger.info("Converting cleaned data to DataFrame...")
        df_cleaned = pd.DataFrame(cleaned_delays)  # Convert list to DataFrame

        cleaned_delays_path = os.path.join(OUTPUT_DIR, "cleaned_delays_data.csv")
        df_cleaned.to_csv(cleaned_delays_path, index=False)
        logger.info("Cleaned delays data saved to %s", cleaned_delays_path)
    else:
        logger.warning("No cleaned delays data found. Nothing to save.")
        
    # ✅ Save records with missing actual arrivals separately
    if missing_actual_arrival:  # Check if list is not empty
        df_missing = pd.DataFrame(missing_actual_arrival)  # Convert list to DataFrame
        missing_path = f"{OUTPUT_DIR}/missing_actual_arrivals.csv"
        df_missing.to_csv(missing_path, index=False)
        logging.warning("⚠️ %s records with missing actual arrival times saved to %s", len(missing_actual_arrival), missing_path)
    
    return df_cleaned

# Now data is ready for merging with geospatial coordinates!