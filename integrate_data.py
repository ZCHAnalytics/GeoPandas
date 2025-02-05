# intergrate_data.py

import pandas as pd

# Step 2.1: Load the train arrival data
train_data_path = "outputs/cleaned_data.csv"  
df_train = pd.read_csv(train_data_path)
print("Train Arrival Data Preview:")
print(df_train.head())

# Step 2.2: Load the station geospatial data
station_data_path = "data/station_coordinates.csv"  
df_coords = pd.read_csv(station_data_path)
print("\nStation Coordinate Data Preview:")
print(df_coords.head())

# Step 2.3: 
# Merge the DataFrames for origin stations 
df_train_origin = pd.merge(df_train, df_coords, left_on="origin", right_on="station_name", how="left", suffixes=("", "_origin"))

# Rename CRS and coordinates columns for origin stations
df_train_origin.rename(columns={"crs": "origin_crs", "latitude": "origin_latitude", "longitude": "origin_longitude"}, inplace=True)

# Merge the new dataset with destination stations data 
df_train_merged = pd.merge(df_train_origin, df_coords, left_on="destination", right_on="station_name", how="left", suffixes=("", "_dest"))

# Rename CRS and coordinates columns for destination
df_train_merged.rename(columns={"crs": "destination_crs", "latitude": "destination_latitude", "longitude": "destination_longitude"}, inplace=True)

# Drop redundant duplicate station_name columns that came from the merge
df_train_merged.drop(columns=["station_name", "station_name_dest"], inplace=True)

# Step 2.5 Save the merged DataFrame to a new CSV file
merged_data_path = "outputs/merged_train_station_data.csv"
df_train_merged.to_csv(merged_data_path, index=False)

print(f"\nMerged data saved to {merged_data_path}")
