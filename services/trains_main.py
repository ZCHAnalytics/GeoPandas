# trains_main.py - Fetch train arrival times from Realtime Trains API

import requests
import sys
import os
import json

# ✅ Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_URL, RTT_USERNAME, RTT_PASSWORD        

def get_train_arrivals(station: str, date: str):
    """
    Fetch train arrivals at a given station on a given date.
    Args:
        station (str): Station code as string (e.g., "FPK").
        date (str): Date in YYYY-MM-DD format.

    Returns:
        dict: JSON response with filtered train arrivals or an error message.
    """
    # ✅ Convert "YYYY-MM-DD" to "YYYY/MM/DD" to match Realtime Trains format
    year, month, day = date.split("-")
    request_url = f"{BASE_URL}/{station}/{year}/{month}/{day}/arrivals"

    try:
        response = requests.get(request_url, auth=(RTT_USERNAME, RTT_PASSWORD))
        response.raise_for_status()
        response_json = response.json()

        # ✅ Debugging: Print total number of services and top-level keys of API response
        total_services = len(response_json.get("services", []))
        print(f"Total Services from API: {total_services}")
        print("🚆 API Response Keys:", list(response_json.keys()))

        # ✅ Ensure 'services' exist in the response
        if "services" not in response_json:
            return {"error": "No 'services' key found in API response"}

        arrivals = []  # Store filtered arrivals

        for service in response_json["services"]:
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

        print(f"✅ Filtered {len(arrivals)} arrivals at {station} for {date}")

        return {"services": arrivals} if arrivals else {"error": "No valid arrivals found"}

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {e}")
        return {"error": f"Failed to fetch train data: {str(e)}"}
