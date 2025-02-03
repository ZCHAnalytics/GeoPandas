# trains_main.py - Fetch train arrival times from Realtime Trains API

import requests
import sys
import os
import logging

# ✅ Add project root directory to Python path
# TODO: Remove the following sys.path modification once the project is properly packaged
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_URL, RTT_USERNAME, RTT_PASSWORD        

# Set up logging v3
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_train_arrivals(station: str, date: str):
    """
    Fetch train arrivals at a given station on a given date.
    Args:
        station (str): Station code as string (e.g., "FPK").
        date (str): Date in YYYY-MM-DD format.

    Returns:
        dict: JSON response with train arrivals or an error message.
    """
    # ✅ Validate and convert "YYYY-MM-DD" to "YYYY/MM/DD" to match Realtime Trains format
    try: 
        year, month, day = date.split("-")
    except ValueError:
        logger.error("Invalid date format provided: %s", str(date))
        return {"error": "Invalid date format. Please use YYYY-MM-DD."}
    
    # ✅ Build the request URL
    request_url = f"{BASE_URL}/{station}/{year}/{month}/{day}/arrivals"
    logger.info("Requesting train arrivals with URL: %s", request_url)
    try:
        response = requests.get(request_url, auth=(RTT_USERNAME, RTT_PASSWORD))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error("❌ API Request Failed: %s", e)
        return {"error": f"Failed to fetch train data: {str(e)}"}
    
    try:
        response_json = response.json()
    except ValueError as e:
        logger.error("Invalid JSON response: %s", e)
        return {"error": "Invalid JSON response from Realtime Trains API."}


    # ✅ Debugging: Print total number of services and top-level keys of API response
    services = response_json.get("services", [])
    logger.info("Total Services from API: %d", len(services))
    logger.info("🚆 API Response Keys:", list(response_json.keys()))

    # ✅ Ensure 'services' exist in the response
    if "services" not in response_json:
        logger.error("No 'services' key found in API response.")
        return {"error": "No 'services' key found in API response."}

    arrivals = []  # Store filtered arrivals

    for service in services:
        loc = service.get("locationDetail", {})

        # ✅ Ensure we only include arrivals at the searched station
        if loc.get("crs") == station:
            arrivals.append({        
                "run_date": service.get("runDate"),
                "service_id": service.get("serviceUid"),
                "operator": service.get("atocName"),
                "is_passenger_train": service.get("isPassenger", False),

                # Scheduled & actual arrival times
                "scheduled_arrival": loc.get("gbttBookedArrival"),
                "actual_arrival": loc.get("realtimeArrival"),
                "is_actual": loc.get("realtimeArrivalActual", False),
                "next_day_arrival": loc.get("realtimeArrivalNextDay", False),

                # Extract origin & destination station names
                "origin": loc.get("origin", [{}])[0].get("description", "UNKNOWN") if loc.get("origin") else "UNKNOWN",
                "destination": loc.get("destination", [{}])[0].get("description", "UNKNOWN") if loc.get("destination") else "UNKNOWN",

                # Additional info
                "was_scheduled_to_stop": loc.get("isCall", False),
                "stop_status": loc.get("displayAs", "UNKNOWN")
            })

    logging.info("✅ Filtered %d arrivals at %s", len(arrivals), str(date))
    return {"services": arrivals} if arrivals else {"error": "No valid arrivals found"}


