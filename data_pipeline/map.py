# geospatial/mapping.py
import folium
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os 

# Ensure the maps folder exists at the project root.
output_dir = os.path.join(os.path.dirname(__file__), '..', 'maps')
os.makedirs(output_dir, exist_ok=True)

# Define the path for the map file.
map_output_path=os.path.join(output_dir, "train_delays_maps.html")

# Example: Doogal Coordinates for Finsbury Park
FPK_latitude = 51.5643002449157
FPK_longitude = -0.106284978884699

def generate_html_map(data):
    # Create a folium map centred at Finsbury Park with an appropriate zoom level
    m = folium.Map(location=[FPK_latitude, FPK_longitude], zoom_start=10)

    #   Add markers to the map for origin stations from the merged dataset.
    for _, row in data.iterrows():

        # skip rows with missing coordinates #TODO
        if pd.isnull(row['origin_latitude']) or pd.isnull(row['origin_longitude']):
            print(f"Skipping marker for {row['origin']} due to missing coordinatrs")
            continue

        popup_info = (
            f"<b>Origin:</b> {row['origin']} (CRS: {row['origin_crs']})<br>"
            f"<br>Destination:</br> {row['destination']} (CRS: {row['destination_crs']})<br>"
            f"<b>Note:</b> Delay information refers to arrivals at Finsbury Park.<br>"  # Added this line
        )    
        
        if "delay_minutes" in row and pd.notnull(row['delay_minutes']):
            delay = row['delay_minutes']
            if delay < 0:
                popup_info += f"<b>Early:</b> {abs(delay)} min"
            else:
                popup_info += f"<b>Delay:</b> {delay} min"

        # Set marker colour based on delay severity
        marker_color = "green" if delay < 0 else "red" if delay > 10 else "orange"
        folium.Marker(
            location=[row['origin_latitude'], row['origin_longitude']],
            popup=folium.Popup(popup_info, max_width=300),
            icon=folium.Icon(color=marker_color, icon="info-sign")
        ).add_to(m)

        # Destination marker with blue icon
        folium.Marker(
            location=[row['destination_latitude'], row['destination_longitude']],
            popup=f"Destination: {row['destination']} (CRS: {row['destination_crs']})",
            icon=folium.Icon(color="blue", icon="flag")
        ).add_to(m)
        
        # Add a title (disclaimer) on the map 
        folium.Marker(
            location=[FPK_latitude, FPK_longitude], 
            popup="<b>Note:</b> Delays shown are for arrivals at Finsbury Park.",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

        # Add a legend 
        legend_html = """
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 250px; height: 100px; 
                        border:2px solid grey; z-index:9999; font-size:14px; 
                        background-color:white; padding: 10px;">
            <b>Legend:</b><br>
            <i class="fa fa-circle" style="color:green"></i> Early<br>
            <i class="fa fa-circle" style="color:orange"></i> On Time<br>
            <i class="fa fa-circle" style="color:red"></i> Delayed<br>
            <br><b>Note:</b> Delays refer to arrivals at Finsbury Park.
            </div>
        """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save the map and return the path where it's saved    
    map_output_path = os.path.join(output_dir, "train_delays_maps.html")
    m.save(map_output_path)
    return map_output_path
    

if __name__ == "__main__":
    merged_data_path = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'merged_train_station_data.csv')
    df_merged = pd.read_csv(merged_data_path)
    print(df_merged.head())

    if not df_merged.empty:
        m = generate_html_map(df_merged)
        m.save(map_output_path)
        print("Map saved to", map_output_path)
    else:
        print("Warning: No merged station data available. Map will be empty.")