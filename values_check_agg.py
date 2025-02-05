import pandas as pd

# Load the merged dataset for checking
df_rtt = pd.read_csv("outputs/merged_train_station_data.csv")

# 1. Group by station
# missing_origin = df[df['origin_crs'].isna()]['origin'].value_counts()
# missing_destination = df[df['destination_crs'].isna()]['destination'].value_counts()

# print("Aggregated stations with missing origin CRS:\n", missing_origin)
# print("Aggregated stations with missing destination CRS:\n", missing_destination)

# 2. Identify if there are names variations in RTT data  
origin_kings_cross = df_rtt[df_rtt['origin'].str.contains("Kings Cross", case=False, na=False)]
origin_letchworth = df_rtt[df_rtt['origin'].str.contains("Letchworth", case=False, na=False)]

destination_kings_cross = df_rtt[df_rtt['destination'].str.contains("Kings Cross", case=False, na=False)]
destination_letchworth = df_rtt[df_rtt['destination'].str.contains("Letchworth", case=False, na=False)]

# Print out the exact station names from the 'origin' and 'destination' columns for each filtered case
print("Stations with 'Kings Cross' in the origin:")
print(origin_kings_cross[['origin']].drop_duplicates())  # Drop duplicates to show unique names

print("\nStations with 'Letchworth' in the origin:")
print(origin_letchworth[['origin']].drop_duplicates())  # Drop duplicates to show unique names

print("\nStations with 'Kings Cross' in the destination:")
print(destination_kings_cross[['destination']].drop_duplicates())  # Drop duplicates to show unique names

print("\nStations with 'Letchworth' in the destination:")
print(destination_letchworth[['destination']].drop_duplicates())  # Drop duplicates to show unique names


