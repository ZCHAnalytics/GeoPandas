# services/delays.py

import pandas as pd 
from services.realtime_trains import get_train_services
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
            booked_str = service["locationDetail"].get("gbttBookedArrival")  # "HHMM" string from response_json
            actual_str = service["locationDetail"].get("realtimeArrival")  # "HHMM" string from response_json
            arrival_confirmed = service["locationDetail"].get("arrival_confirmed", False)

            if booked_str and actual_str and arrival_confirmed and converted_date:
                # Convert time to minutes since midnight
                try:
                    booked_minutes = int(booked_str[:2]) * 60 + int(booked_str[2:])
                    actual_minutes = int(actual_str[:2]) * 60 + int(actual_str[2:])
                    if actual_minutes < booked_minutes and actual_minutes < 300:
                        actual_minutes += 1440
        
                        delay_minutes = actual_minutes - booked_minutes



                    delay_data.append({
                        "date": converted_date,
                        "train_number": service["trainIdentity"],
                        "operator": service["atocName"],
                        "origin": origin,
                        "destination": destination,
                        "scheduled_arrival": booked_str,
                        "actual_arrival": actual_str,
                        "delay_minutes": delay_minutes
                    })
                except ValueError:
                    continue 

    print(f"\n Total Delays found: {len(delay_data)}\n")
    return pd.DataFrame(delay_data)
