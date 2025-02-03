# geospatial/mapping.py

import folium
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os 
from get_spatial_data import get_station_data


# Ensure the geodata folder exists at the project root.
output_dir = "geodata"
os.makedirs(output_dir, exist_ok=True)

# Define the path for the map file.
map_output_path = os.path.join(output_dir, "stations_map.html")


# Example: Coordinates for Finsbury Park
FPK_latitude = 51.5720
FPK_longitude = -0.1053

def create_base_map():
    """
    Creates a base map centred on Finsbury Park.
    """
    # Create a folium map centred at Finsbury Park with an appropriate zoom level
    base_map = folium.Map(location=[FPK_latitude, FPK_longitude], zoom_start=14)
    return base_map

def add_markers(map_object, data):    
    """
    Add markers to the map from a DataFrame.
    
    Expects a DataFrame with columns:
      - 'latitude': The latitude coordinate of the station.
      - 'longitude': The longitude coordinate of the station.
      - 'station_name': The name of the station.
      - 'crs': The CRS code of the station.
      
    Each marker popup will display the station name and its CRS code.
    """

    for _, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['station_name']} (CRS: {row['crs']})"
        ).add_to(map_object)
    return map_object

if __name__ == "__main__":
    # Retrieve station data (this function should download or load the station data)
    df_stations = get_station_data()
    print("DataFrame columns:", df_stations.columns)
    print("DataFrame head:\n", df_stations.head())


    # Create the base map 
    m = create_base_map()

    # If there is station data, add markers to the map
    if not df_stations.empty:
        m = add_markers(m, df_stations)
    else:
        print("Warning: No station data available. Map will be empty.")

    # Save the map to an HTML file
    m.save(map_output_path)
    print("Map saved to", map_output_path)
