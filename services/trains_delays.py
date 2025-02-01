# services/delays.py

import pandas as pd 
from services.trains_main import get_train_services
from datetime import datetime, timedelta


def get_delays_info(origin, destination, past_days=6):
    delay_data = []

    # Get data for the last `past_days` days
    for day in range(past_days):
        date = pd.to_datetime("today") - timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")

        response_json = get_train_services(origin, destination, date_str)

        if not response_json or "services" not in response_json:
            continue

        for service in response_json["services"]:
            run_date = service.get("runDate")
            converted_date = datetime.strptime(run_date, "%Y-%m-%d").date() if run_date else None

            location = service["locationDetail"] # already process
            if location["gbttBookedArrival"] and location ["realtimeArrival"] and location["delay_minutes"] is not None:
            
                delay_data.append({
                    "date": converted_date,
                    "train_number": service["trainIdentity"],
                    "operator": service["atocName"],
                    "origin": origin,
                    "destination": destination,
                    "scheduled_arrival": location["gbttBookedArrival"],
                    "actual_arrival": location["realtimeArrival"],
                    "delay_minutes": location["delay_minutes"]
                })

    print(f"\n Total Delays found: {len(delay_data)}\n")
    return pd.DataFrame(delay_data)
