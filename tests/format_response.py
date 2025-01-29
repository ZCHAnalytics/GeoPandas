import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI

load_dotenv()

USERNAME = os.getenv("RTT_USERNAME")
PASSWORD = os.getenv("RTT_PASSWORD")
ENDPOINT = os.getenv("RTT_ENDPOINT")

base_url=f"https://{ENDPOINT}/json/search/"

app = FastAPI()

@app.get("/api/trains")
def get_train_services(origin: str, destination: str):
    """
    Get trains servicesbetween two stations from the Realtime Trains API 
    """

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