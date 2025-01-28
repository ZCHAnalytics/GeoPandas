import os
from dotenv import load_dotenv
import requests

from fastapi import FastAPI
import requests

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

@app.get("/")
async def root(): # Root endpoint to confirm the service is running
    return {"message": "Realtime Train API service is running!"}
