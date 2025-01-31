# realtime_trains.py

import requests
from datetime import datetime
from config import BASE_URL, RTT_USERNAME, RTT_PASSWORD
    
## endpoint for train services between two stations 
def get_train_services(origin: str, destination: str, date: str):

    # Validate date format 
    if not (len(date) == 10 and date[4] == "-" and date[7] == "-"):
        return {"error": "Invalid data format. Use YYYY-MM-DD"}
    
    request_url = f"{BASE_URL}/{origin}/to/{destination}/{date[:4]}/{date[5:7]}/{date[8:]}"
    response = requests.get(request_url, auth=(RTT_USERNAME, RTT_PASSWORD))
    
    if response.status_code != 200:
        return {
            "error": f"Failed to get train data. HTTP {response.status_code}",
            "details": response.text
        }
    
    response_json = response.json()
    print(f"RTT API response for {date}: {len(response_json.get('services', []))} services")

    for service in response_json.get("services", []):
        if "locationDetail" in service:
            location = service["locationDetail"]
            location["arrival_confirmed"] =location.get("realtimeArrivalActual", False)
            
    return response_json