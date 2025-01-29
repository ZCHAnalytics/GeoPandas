import pandas as pd 
from services.realtime_trains import get_train_services

def get_delays_info(origin, destination, past_days=6):
    delay_data = []

    # If no date is provided, use last 6 days 
    for day in range(past_days):
        date = pd.to_datetime("today") - pd.Timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")
        response_json = get_train_services(origin, destination, date_str)
        if not response_json or "services" not in response_json:
            continue
        for i in response_json["services"]:
            booked_arrival = i["locationDetail"].get("gbttBookedDeparture")
            actual_arrival = i["locationDetail"].get("realtimeArrival")
            if booked_arrival and actual_arrival and actual_arrival.isdigit() and booked_arrival.isdigit():
                delay_minutes = int(actual_arrival) - int(booked_arrival)
                delay_data.append({
                    "date": date_str,
                    "train_number": i["trainIdentity"],
                    "operator": i["atocName"],
                    "scheduled_arrival": booked_arrival,
                    "actual_arrival": actual_arrival,
                    "delay_minutes": delay_minutes
                })
                
    return pd.DataFrame(delay_data)