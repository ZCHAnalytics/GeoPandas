# clean.py - Process & clean train data

import pandas as pd
from datetime import datetime, timedelta
import os

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
    cleaned_data = []
    missing_actual_arrival = [] # Store records with missing actual_arrival

    for service in raw_data.get("services", []):
        # Extract top-level fields:
        run_date = service.get("run_date")
        service_id = service.get("service_id")
        operator = service.get("operator")
        is_passenger_train = service.get("is_passenger_train")

        # Ensure date is correctly formatted
        if run_date:
            try:
                converted_date = datetime.strptime(run_date, "%Y-%m-%d").date()
            except ValueError:
                print(f"❌ Invalid runDate format: {run_date}")
                continue  # Skip invalid dates
        
        # ✅ Extract core arrival details 
        scheduled_arrival = service.get("scheduled_arrival")
        actual_arrival = service.get("actual_arrival")
        is_actual = service.get("is_actual", False)
        next_day_arrival = service.get("next_day_arrival")

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
                "next_day_arrival": next_day_arrival,
                "origin": origin,
                "destination": destination,
                "was_scheduled_to_stop": was_scheduled_to_stop,
                "stop_status": stop_status,
                "delay_minutes": None
            })
            continue  # Skip this record for the main cleaned dataset
        
        # ✅ Convert HHMM strings to time objects
        try:
            scheduled_time = datetime.strptime(scheduled_arrival, "%H%M").time()
            actual_time = datetime.strptime(actual_arrival, "%H%M").time()
        except ValueError:
            print(f"❌ Invalid time format: {scheduled_arrival}, {actual_arrival}")
            continue  # Skip invalid time formats

        # ✅ Handle past-midnight arrivals (actual before 05:00 but scheduled before midnight)
        if actual_time.hour < 5 and scheduled_time.hour > 20:
            converted_date += timedelta(days=1)
            
# ✅ Calculate delay in minutes
        delay_minutes = (datetime.combine(converted_date, actual_time) -
                         datetime.combine(converted_date, scheduled_time)).total_seconds() // 60

        # ✅ Append cleaned data
        cleaned_data.append({
            "run_date": run_date,
            "service_id": service_id,
            "operator": operator,
            "is_passenger_train": is_passenger_train,
            "scheduled_arrival": scheduled_time.strftime("%H:%M"),
            "actual_arrival": actual_time.strftime("%H:%M"),
            "is_actual": is_actual,
            "next_day_arrival": next_day_arrival,
            "origin": origin,
            "destination": destination,
            "was_scheduled_to_stop": was_scheduled_to_stop,
            "stop_status": stop_status,
            "delay_minutes": int(delay_minutes)
        })

    # ✅ Convert to DataFrame
    df_clean = pd.DataFrame(cleaned_data)
    df_missing = pd.DataFrame(missing_actual_arrival)

    # ✅ Save cleaned data
    cleaned_path = f"{OUTPUT_DIR}/cleaned_data.csv"
    df_clean.to_csv(cleaned_path, index=False)
    print(f"✅ Cleaned data saved to {cleaned_path}")

    # ✅ Save records with missing actual arrivals separately
    if not df_missing.empty:
        missing_path = f"{OUTPUT_DIR}/missing_actual_arrivals.csv"
        df_missing.to_csv(missing_path, index=False)
        print(f"⚠️  {len(df_missing)} records with missing actual arrival times saved to {missing_path}")

    return df_clean