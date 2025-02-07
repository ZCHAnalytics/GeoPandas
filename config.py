# config.py file
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
# Retrieve environment variables 
RTT_USERNAME = os.getenv("RTT_USERNAME")
RTT_PASSWORD = os.getenv("RTT_PASSWORD")
RTT_ENDPOINT = os.getenv("RTT_ENDPOINT")

BASE_URL=f"https://{RTT_ENDPOINT}/json/search/"

# Ensure credentials are set
if not RTT_USERNAME or not RTT_PASSWORD or not RTT_ENDPOINT:
    raise ValueError("Missing environment credentials")