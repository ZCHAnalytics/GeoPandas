# 01_api_call.py - Test RTT API and Save Data

from services.trains_main import get_train_services
import json 

# Set test parameters
origin = "FPK"
destination = "KGX"
date = "2025-01-29"  

# call API and retrive json response 
rtt_json = get_train_services(origin, destination, date)

# 1. Print all top-level keys in the API response
if isinstance(rtt_json, dict) and len(rtt_json) > 0: 
    # Check if rtt_json is a dictionary AND has at least one key-value pair
    print("\n✅ API response keys:", list(rtt_json.keys()))  # ✅ Print all keys
    
    first_key = next(iter(rtt_json))  # Create an iterator over the dictionary keys and retrieve the first next key
    print(f"✅ First key in API response: {first_key}")
    
else:
    print("❌ API response is empty or not a dictionary.")

# 2. Print a sample of the first next key data
sample_key = first_key #use the first key dynamically 
if sample_key in rtt_json:
    print("\n Sample data from '{sample_key}':\n", json.dumps(rtt_json[sample_key], indent=4)) 
