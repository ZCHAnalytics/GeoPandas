# test file for dataframe
import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI
from datetime import datetime, timedelta
import pandas as pd 

load_dotenv()

USERNAME = os.getenv("RTT_USERNAME")
PASSWORD = os.getenv("RTT_PASSWORD")
ENDPOINT = os.getenv("RTT_ENDPOINT")

base_url=f"https://{ENDPOINT}/json/search/"
    
app = FastAPI()

# Endpoint for delays info
@app.get("/api/delays")
def get_delays_info(origin:str, destination: str, date: str = None):
    delay_data = []
    # If no date is provided, use last 6 days 
    if not date:
        past_6_days = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6)]
    else: 
        past_6_days = [date] # fetch data for the sepcified date 

    for day in past_6_days:
        response = requests.get(f"{base_url}/{origin}/to/{destination}/{day[:4]}/{day[5:7]}/{day[8:]}", auth=(USERNAME, PASSWORD))
        response_json = response.json() # Convert response to JSON 
        # Extract departure and arrival times, operator, train number
        for i in response_json.get("services", []): # Handle missing services
            booked_arrival = i["locationDetail"].get("gbttBookedDeparture")
            actual_arrival = i["locationDetail"].get("realtimeArrival")
            if booked_arrival and actual_arrival and actual_arrival.isdigit() and booked_arrival.isdigit():
                delay_minutes = int(actual_arrival) - int(booked_arrival)
                delay_data.append({
                    "date": day,
                    "train_number": i["trainIdentity"],
                    "operator": i["atocName"],
                    "scheduled_arrival": booked_arrival,
                    "actual_arrival": actual_arrival,
                    "delay_minutes": delay_minutes
            })
    df = pd.DataFrame(delay_data)    
    print(f"Total delayed trains found: {len(delay_data)}")
    return df.to_dict(orient="records")