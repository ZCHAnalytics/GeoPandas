# realtime_trains.py - Fetch train arrival times from Realtime Trains API

import requests
from datetime import datetime, timedelta
from config import BASE_URL, RTT_USERNAME, RTT_PASSWORD

# 1️⃣ Convert time strings (HHMM) from RTT API to datetime.time
def convert_to_time(value):
    try:
        return datetime.strptime(value, "%H%M").time() if value else None
    except (ValueError, TypeError):
        return None # Handle invalid/missing values 
    
# 2️⃣ Calculate delay, handling after-midnight arrivals
def calculate_delay(scheduled_arrival, actual_arrival, is_actual):
    """
    Calculate delay in minutes, handling cases where a train arrives after midnight.

    Args:
        scheduled_arrival (str): Scheduled arrival time (HHMM).
        actual_arrival (str): Actual arrival time (HHMM).
        is_actual (bool): Whether the actual arrival time is confirmed (not estimated).

    Returns:
        int: Delay in minutes, or None if actual arrival isn't confirmed.
    """
    if not is_actual: # if actual arrival isn't confirmed, no need to calculate delay 
        return None 
    scheduled = convert_to_time(scheduled_arrival) # use first function 
    actual = convert_to_time(actual_arrival) # use first function 

    if not scheduled or not actual:
        return None # if times are invalid
    
    # Convert to datetime objects (using today's date) 
    base_date = datetime.today().date()
    scheduled_dt = datetime.combine(base_date, scheduled)
    actual_dt = datetime.combine(base_date, actual)

    # Handle after midnight arrival (actual before 05:00 but schedule before midnight the previous day)
    if actual.hour < 5 and scheduled.hour > 20:
        actual_dt += timedelta(days=1) # Move actual arrival to the next day
        
    # Calculate delay
    delay_minutes = (actual_dt - scheduled_dt).total_seconds() // 60
    return int(delay_minutes)

# 3️⃣ Extract arrival details from API response
def extract_location_details(service):
    """
    Extract and process arrival details from a train service entry.
    
    Args:
        service (dict): Train service JSON object.
    
    Returns:
        dict: Processed location details including converted times and delay.
    """
    location = service.get("locationDetail", {})

    scheduled_arrival = location.get("gbttBookedArrival")
    actual_arrival = location.get("realtimeArrival")
    is_actual = location.get("realtimeArrivalActual", False)  # Use correct key

    location["gbttBookedArrival"] = convert_to_time(scheduled_arrival)
    location["realtimeArrival"] = convert_to_time(actual_arrival)
    location["delay_minutes"] = calculate_delay(scheduled_arrival, actual_arrival, is_actual)

    return location

# 3️⃣ Extract arrival details from API response
def get_train_services(origin: str, destination: str, date: str):
    """
    Fetch train services between two stations on a given date.

    Args:
        origin (str): Origin station code.
        destination (str): Destination station code.
        date (str): Date in YYYY-MM-DD format.

    Returns:
        dict: JSON response from the RTT API or an error message.
    """
    request_url = f"{BASE_URL}/{origin}/to/{destination}/{date.replace('-', '/')}"

    try:
        response = requests.get(request_url, auth=(RTT_USERNAME, RTT_PASSWORD))
        response.raise_for_status() # Raise an error if request fails
        response_json = response.json() 
        print("\n Raw API Response Keys:", list(response_json.keys())) # Debugging and checking dictionary key structure


        # Process all arrivals using a helper fuction to reduce code duplication          
        for service in response_json.get("services", []):
            service["locationDetail"] = extract_location_details(service)
        
        return response_json
    
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}") 
        return {"error": f"Failed to fetch train data: {str(e)}"}
