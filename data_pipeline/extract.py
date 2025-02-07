# Extract raw data and save locally

import json
import sys
import os
import logging
from datetime import datetime, timedelta

# ✅ Add project root directory to Python path
# TODO: Remove the following sys.path modification once the project is properly packaged
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.trains_main import get_train_arrivals  # Import function

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ✅ Define output directory
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Create the folder if it doesn't exist

def extract_data(station: str, days: int = 7) -> dict:
    all_data = {"services": []} # Initialise empty contrainer

    for i in range(days):
        # Calculate the date string for 'i' days ago
        date =  (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        #logger.info("Fetching data for %s...", str(date))

        raw_data = get_train_arrivals(station, date)
    
        if raw_data and "services" in raw_data:
             # Append to full dataset
            all_data["services"].extend(raw_data["services"]) # Append to full dataset 
        else: 
            logger.error("❌ No valid train data found for %s on %s", station, str(date))
            
    # ✅ Save combined JSON
    output_path = f"outputs/raw_data_{station}.json"
    with open(output_path, "w") as f:
        json.dump(raw_data, f, indent=4)
    logger.info("Raw data saved to %s", output_path)
    logging.info("✅ Extracted %d total train records over %d days.", len(all_data["services"]), days)
    
    return all_data

# ✅ Call the function when script runs
if __name__ == "__main__":
    # station = "FPK"  # ✅ Default: Finsbury Park
    # extracted_data = extract_data(station, days=7)

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

