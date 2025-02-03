# extract.py - Extract raw data and save locally

import json
import sys
import os
from datetime import datetime, timedelta

# ✅ Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.trains_main import get_train_arrivals  # Import function

# ✅ Define output directory
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Create the folder if it doesn't exist

def extract_data(station: str, days: int=7):
    all_data = {"services": []} # Initialise empty contrainer

    for i in range(days):
        date =  (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        print(f" Fetching data for {date}...")

        raw_data = get_train_arrivals(station, date)
    
        if raw_data and "services" in raw_data:
            all_data["services"].extend(raw_data["services"]) # Append to full dataset 
        else: 
            print(f"❌ No valid train data found for {station} on {date}")
            
    # ✅ Save combined JSON
    output_path = f"outputs/raw_data_{station}.json"
    with open(output_path, "w") as f:
        json.dump(raw_data, f, indent=4)
    print(f"raw data saved to {output_path}")

    print(f"✅ Extracted {len(all_data)} total train records over {days} days.")
    return all_data

# ✅ Call the function when script runs
if __name__ == "__main__":
    station = "FPK"  # ✅ Default: Finsbury Park
    extracted_data = extract_data(station, days=7)


""" Testing block for deletion

def extract_raw_data(station, date):
    Extracts full API response without filtering.
    raw_data = get_train_arrivals(station, date)

    # ✅ Save unfiltered JSON response
    raw_output_path = f"outputs/raw_data_{station}_{date}.json"
    with open(raw_output_path, "w") as f:
        json.dump(raw_data, f, indent=4)

    print(f"✅ Raw unfiltered data saved to {raw_output_path}")

    return raw_data


# ✅ Run extraction when script is executed
if __name__ == "__main__":
    station = "FPK"  # Example: Finsbury Park
    date = "2025-01-31"

    raw_data = extract_raw_data(station, date)

    # ✅ Debugging: Print number of total services
    print(f"🚆 Extracted {len(raw_data.get('services', []))} train records")
"""

