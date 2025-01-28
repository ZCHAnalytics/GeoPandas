import os
from dotenv import load_dotenv
import requests

#Load environment varialbes from .env file
load_dotenv()

# Retrieve environment variables 
USERNAME = os.getenv("RTT_USERNAME")
PASSWORD = os.getenv("RTT_PASSWORD")
ENDPOINT = os.getenv("RTT_ENDPOINT")

# Ensure credentials are set
if not USERNAME or not PASSWORD or not ENDPOINT:
    raise EnvironmentError("missing environment credentials")

RTT_URL=f"https://{ENDPOINT}/json/search/LST/to/GTW"

def test_connection():
    
    try:
        response = requests.get(RTT_URL, auth=(USERNAME, PASSWORD))
        response.raise_for_status()
        data = response.json()
        print("Connection successful!")
    except requests.exceptions.RequestException as e:
        print("Connection failed")
        print("Error", e)

if __name__=="__main__":
    test_connection()