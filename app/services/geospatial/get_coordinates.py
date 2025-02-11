# Get Spatial Data 

import os
import requests
import json
import pandas as pd

from app.core.logging_config import configure_logging

logger = configure_logging()

# Define paths for storing data
DATA_DIR = "data"
STATION_JSON_PATH = os.path.join(DATA_DIR, "station_data.json") # Retrieved data 
STATION_CSV_PATH = os.path.join(DATA_DIR, "station_coordinates.csv") # Processed data 
os.makedirs(DATA_DIR, exist_ok=True)

# Function for retrieving data from public sources
def fetch_station_data_from_url():
    url = "https://www.doogal.co.uk/UkStationsKML/?output=json"
    response = requests.get(url)
    if response.status_code == 200:
        station_data = response.json()
        print("Downloaded JSON with keys:", list(station_data.keys()))
        with open(STATION_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(station_data, f, indent=2)
        return station_data
    else:
        print("Failed to download data. Status code:", response.status_code)
        return None
    
# Function for processing data and storing results in CSV file 
def extract_station_coordinates(station_data):
    features = station_data.get("features", [])
    records = []
    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [None, None])
        record = {
            "crs": properties.get("code"),
            "station_name": properties.get("name"),
            "longitude": coords[0],
            "latitude": coords[1],
        }
        records.append(record)
    print(f"Processed {len(records)} records from JSON.")
    df_stations = pd.DataFrame(records)
    df_stations.to_csv(STATION_CSV_PATH, index=False)
    print(f"CSV saved to: {STATION_CSV_PATH} with {len(df_stations)} rows.")
    return df_stations

# Function to call first two functions in the correct order and skipping download fuction if CSV already exists
def load_extracted_coordiantes_data():
    # Check current working directory (for debugging)
    print("Current working directory:", os.getcwd())
    # Optionally, force re-download if CSV exists but is empty.
    if os.path.exists(STATION_CSV_PATH):
        if os.path.getsize(STATION_CSV_PATH) == 0:
            print("Existing CSV is empty. Forcing re-download.")
            station_data = load_extracted_coordiantes_data() # Fetch JSON from doogal
            if station_data:
                df = extract_station_coordinates(station_data)
            else:
                df = pd.DataFrame()
        else:
            print("Loading station data from CSV.")
            df = pd.read_csv(STATION_CSV_PATH)
    else:
        station_data = load_extracted_coordiantes_data()
        if station_data:
            df = exit(station_data) # Extract station names, CRS codes, latitudes and longitudes 
        else:
            df = pd.DataFrame()
    return df # New or Existing DataFrame

if __name__ == "__main__":
    df = load_extracted_coordiantes_data()
    print("Final DataFrame preview:")
    print(df.head())
