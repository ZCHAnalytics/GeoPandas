import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI
from datetime import datetime, timedelta
import pandas as pd 

# Load environment varialbes from .env file
load_dotenv()

# Retrieve environment variables 
USERNAME = os.getenv("RTT_USERNAME")
PASSWORD = os.getenv("RTT_PASSWORD")
ENDPOINT = os.getenv("RTT_ENDPOINT")

# Ensure credentuas are set
if not USERNAME or not PASSWORD or not ENDPOINT:
    raise EnvironmentError("missing environment credentials")

base_url=f"https://{ENDPOINT}/json/search/"
    
# Instantiate FastAPI app
app = FastAPI()
"""
# Endpoint for train info
@app.get("/api/trains")
def get_train_services(origin: str, destination: str):
    
    # Get trains servicesbetween two stations from the Realtime Trains API 
    
    response = requests.get(f"{base_url}/{origin}/to/{destination}", auth=(USERNAME, PASSWORD))
    response_json = response.json() # Convert response to JSON 
    train_list = [] # List to store extracted train details
    # Print only first 50 lines for debugging   
    print("\n".join(str(response_json).split("\n")[:50])) 

    # Extract departure and arrival times, operator, train number
    for i in response_json["services"]:
        departure = i["locationDetail"]["gbttBookedDeparture"]  
        arrival = i["locationDetail"]["destination"][0]["publicTime"] 
        operator = i["atocName"] 
        train_number = i["trainIdentity"]
        train_list.append({
            "departure_time": departure,
            "arrival_time": arrival,
            "operator": operator,
            "train_number": train_number
        })
        
    return train_list
"""
# Endpoint for delays info
@app.get("/api/delays")
def get_delays_info(origin:str, destination: str, date: str = None):
    delay_data = []

    # If not date is provided, use last 7 days 
    if not date:
        past_7_days = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    else: 
        past_7_days = [date] # fetch data for the sepcified date 

    for day in past_7_days:
        response = requests.get(f"{base_url}/{origin}/to/{destination}/{day}", auth=(USERNAME, PASSWORD))
        response_json = response.json() # Convert response to JSON 
        delayed_list = [] # List to store extracted train details

        # Extract departure and arrival times, operator, train number
        for i in response_json["services"]:
            booked_arrival = i["locationDetail"]["gbttBookedDeparture"]
            actual_arrival = i["locationDetail"].get("realtimeArrival")
            if actual_arrival and int(actual_arrival) > int(booked_arrival):
                delay_minutes = int(actual_arrival) - int(booked_arrival)
                print("\nDelays in minutes:", delay_minutes)
                delay_data.append({
                    "date": day,
                    "train_number": i["trainIdentity"],
                    "operator": i["atocName"],
                    "scheduled_arrival": booked_arrival,
                    "actual_arrival": actual_arrival,
                    "delay_minutes": delay_minutes
            })
        df = pd.DataFrame(delay_data)    
        return df.to_dic(orient="records")