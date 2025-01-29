import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI
import requests

load_dotenv()

USERNAME = os.getenv("RTT_USERNAME")
PASSWORD = os.getenv("RTT_PASSWORD")
ENDPOINT = os.getenv("RTT_ENDPOINT")

base_url=f"https://{ENDPOINT}/json/search/"

app = FastAPI()

## endpoint for train services between two stations 
@app.get("/api/trains")
def get_train_services(origin: str, destination: str):
    response = requests.get(f"{base_url}/{origin}/to/{destination}", auth=(USERNAME, PASSWORD))
    return {"data": response.json()}
    
