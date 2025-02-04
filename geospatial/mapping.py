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
# old map # map_output_path = os.path.join(output_dir, "stations_map.html")

# New map - Add delays with merged dataset with crs for origin and destination
map_output_path=os.path.join(output_dir, "train_delays_maps.html")

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

def add_origin_markers(map_object, data):
    """
    Add markers to the map for origin stations from the merged dataset.
    
    Expects the DataFrame to have the following columns:
      - 'origin': The origin station name.
      - 'origin_csr': The CRS code for the origin station.
      - 'origin_latitude': The latitude for the origin station.
      - 'origin_longitude': The longitude for the origin station.
      - 'delay_minutes': The delay in minutes (can be negative if the train arrives early).
      
    Each marker popup will display the origin station name, CRS code, and delay information.
    """
    for _, row in data.iterrows():
        # skip rows with missing coordinates #TODO
        if pd.isnull(row['origin_latitude']) or pd.isnull(row['origin_longitude']):
            print(f"Skipping marker for {row['origin']} due to missing coordinators")
            continue
        popup_info = f"Origin: {row['origin']} (CSR: {row['origin_csr']}"
        if "delay_minutes" in row and pd.notnull(row['delay_minutes']):
            delay = row['delay_minutes']
            if delay < 0:
                popup_info += f"<br>Early by {abs(delay)} min"
            else:
                popup_info += f"<br>Delay: {delay} min"
        folium.Marker(
            location=[row['origin_latitude'], row['origin_longitude']],
            popup=popup_info
        ).add_to(map_object)
    return map_object

def add_destination_markers(map_object, data):
    """
    Add markers to the map for destination stations from merged dataset.

    """
    for _, row in data.iterrows():
        popup_info = f"Destination: {row['destination']} (CSR: {row['destination_csr']}"
        folium.Marker(
            location=[row['destination_latitude'], row['destination_longitude']],
            popup=popup_info,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_object)
    return map_object

if __name__ == "__main__":
    # Load the merged dataset from the outputs folders
    merged_data_path = "outputs/merged_train_station_data.csv"
    df_merged = pd.read_csv(merged_data_path)
    print("Merged DataFrame columns:", df_merged.columns)
    print("Merged DataFrame preview:\n", df_merged.head())

    # Create the base map
    m = create_base_map()

    # Add markers for origin stations
    if not df_merged.empty:
        m = add_origin_markers(m, df_merged)
        # Uncomment the following line for adding destination markers:
        # m = add_destination_markers(m, df_merged)
    else:
        print("Warning: No merged station data availalbe. Map will be empty.")
    
    # Save the map to html file.
    m.save(map_output_path)
    print("Map saved to", map_output_path)

    
""" # Old function before merging datasets 

def add_markers(map_object, data):    
    
    for _, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['station_name']} (CSR: {row['csr']})"
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
"""