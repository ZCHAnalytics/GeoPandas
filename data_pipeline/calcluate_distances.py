# distances.py
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic 

# Load the station dataset (after cleaning)
def load_data(csv_path):
    # Load merged data with stations CRS, longitude and latitude:
    df = pd.read_csv(csv_path)
    df['geometry'] = df.apply(lambda row: Point(row['origin_longitude'], row['origin_latitude']), axis=1)
    print("Available columns:", df.columns)  # Debugging line to check column names    
    return gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

def calculate_distances(df, target_coords, delay_threshold=10):
    
    # Filter stations experiencing frequent delays
    delayed_stations = df[df['delay_minutes'] >= delay_threshold].copy()

    if delayed_stations.empty:
        print("No stations meet the delay threshold.")
        return pd.DataFrame(columns=['origin_crs', 'origin', 'distance_km', delay_col])
    
    delayed_stations['distance_km'] = delayed_stations.geometry.apply(lambda x:geodesic((target_coords[1], target_coords[0]), (x.y, x.x)).km)

    return delayed_stations.sort_values(by='distance_km')


if __name__ == "__main__":
    csv_path = "outputs/merged_train_station_data.csv"
    df = load_data(csv_path)

    target_coords = (-0.106, 51.564) # Finsbury Park's longitude, Latitude , according to doogal: -0.106284978884699,51.5643002449157
    nearest_delayed = calculate_distances(df, target_coords)

    if nearest_delayed.empty:
        print("No delayed stations found.")
    else:
        print(nearest_delayed[['origin_crs', 'origin', 'distance_km', 'delay_minutes']].head(10))
