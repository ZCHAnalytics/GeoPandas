# Merge data 
import pandas as pd
import logging
import os
from fuzzywuzzy import process 

# Set up logging
logger = logging.getLogger("train_api")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def merge_geospatial_data(cleaned_delays): 
    """
    Merge cleaned train arrival data with geospatial station data
    Args: 
        df_delays (pd.DataFrame): Cleaned train data with origins and destinations
    Returns:
        pd.DataFrame: Merged dataset with geospatial coordinates 
    """
    # Step 1: Load the train arrival data
    delays_data_path = "outputs/cleaned_delays_data.csv"  
    df_cleaned_delays = pd.read_csv(delays_data_path)
    #logger.info("Train Arrival Data Preview:")
    #logger.info(df_cleaned_delays.head())
    
    # Step 2: Load the station geospatial data
    coordinates_data_path = "data/station_coordinates.csv"  
    df_coords = pd.read_csv(coordinates_data_path)
    #logger.info("\nStation Coordinate Data Preview:")
    #logger.info(df_coords.head())    


    # Step 3: Identify stations in df_cleaned_delays that are not in df_coord
    # Extract unique station names
    delays_origins = set(df_cleaned_delays["origin"].unique())
    delays_destinations = set(df_cleaned_delays["destination"].unique())
    station_names = set(df_coords["station_name"].unique())

    # Find unmatched origin and destination station names
    unmatched_origins = delays_origins - station_names
    unmatched_destinations = delays_destinations - station_names

    # Log unmatched station names
    if unmatched_origins:
        logger.warning("⚠️ Unmatched origin stations (not in geospatial data):\n%s", unmatched_origins)

    if unmatched_destinations:
        logger.warning("⚠️ Unmatched destination stations (not in geospatial data):\n%s", unmatched_destinations)

    # Step 4: Detect Nnmes variations using partial matches with fuxxywuzzy
    def find_best_matches(unmatched_stations, station_names):
        suggestions = {}
        for station in unmatched_stations:
            match, score = process.extractOne(station, station_names)
            if score > 80:  # Confidence threshold (adjustable)
                suggestions[station] = match
        return suggestions

    # Find possible name variations
    origin_suggestions = find_best_matches(unmatched_origins, station_names)
    destination_suggestions = find_best_matches(unmatched_destinations, station_names)

    # Log potential name mismatches
    if origin_suggestions:
        logger.info("🔍 Suggested name corrections for origin stations: %s", origin_suggestions)
    if destination_suggestions:
        logger.info("🔍 Suggested name corrections for destination stations: %s", destination_suggestions)

    # Step 4: Manually define name corrections for known issues
    name_corrections = {
        "Letchworth": "Letchworth Garden City",
        "London Kings Cross": "King's Cross",
    }

    # Apply corrections to the cleaned data
    df_cleaned_delays["origin"] = df_cleaned_delays["origin"].replace(name_corrections)
    df_cleaned_delays["destination"] = df_cleaned_delays["destination"].replace(name_corrections)

    # Step 6: Merge cleaned data with origin stations coordinates 
    df_origin = pd.merge(df_cleaned_delays, df_coords, left_on="origin", right_on="station_name", how="left", suffixes=("", "_origin"))

    # Rename CRS and coordinates columns for origin stations
    df_origin.rename(columns={"crs": "origin_crs", "latitude": "origin_latitude", "longitude": "origin_longitude"}, inplace=True)

    # Step 7: Merge the new dataset with destination stations data 
    df_merged = pd.merge(df_origin, df_coords, left_on="destination", right_on="station_name", how="left", suffixes=("", "_dest"))

    # Rename CRS and coordinates columns for destination
    df_merged.rename(columns={"crs": "destination_crs", "latitude": "destination_latitude", "longitude": "destination_longitude"}, inplace=True)

    # Drop redundant duplicate station_name columns that came from the merge
    df_merged.drop(columns=["station_name", "station_name_dest"], inplace=True)

    # 🚀 Step 8: Identify Missing CRS Values in cleaned 
    logger.info("🚀 Checking if there are still missing values, dropping Peteboro Maint Shed")

    missing_origin = df_merged[df_merged['origin_crs'].isna()]['origin'].value_counts()
    missing_destination = df_merged[df_merged['destination_crs'].isna()]['destination'].value_counts()

    logger.info("⚠️ Aggregated stations with missing origin CRS:\n%s", missing_origin)
    logger.info("\n⚠️ Aggregated stations with missing destination CRS:\n%s", missing_destination)

    # Step 9: Drop unwanted records such as 'Peterboro Maint Shed which is not a passenger train
    dropped_records_path = "outputs/dropped_records.csv"  # Define path to save dropped records

    def drop_and_log_missing_values_records(df, column, dropped_records_path):
        # find the row with missing values in two specific columns
        missing_records = df[df[column].isna()]

        # if any values missing, save to CSV for inspection
        if not missing_records.empty:
            missing_records.to_csv(dropped_records_path, mode='a', header=not os.path.exists(dropped_records_path), index=False)
            print(f"Dropped {len(missing_records)} record(s) with missing {column} and saved to {dropped_records_path}.")

        # Drop the rows with missing values in the specific column
        return df.dropna(subset=[column])
    
    # Apply function to drop records where origin or destination CRS is missing
    df_merged = drop_and_log_missing_values_records(df_merged, "origin_crs", dropped_records_path)
    df_merged = drop_and_log_missing_values_records(df_merged, "destination_crs", dropped_records_path)

    # Step 10: Debugging: Check duplicate columns and indices
    logger.info("📌 Duplicate columns:\n%s", df_merged.columns[df_merged.columns.duplicated()])
    logger.info("📌 Duplicate indices: %d", df_merged.index.duplicated().sum())

    # Step 11: 🚀 Ensure date columns are converted back to datetime
    df_merged['run_date'] = pd.to_datetime(df_merged['run_date']).dt.date  # Convert to date

    # 🔍 Final check: if arrival times are already in string format
    logger.info("📅 Data types: %s", df_merged.dtypes)
    logger.info("📅 Scheduled & Actual Arrival Times Preview:\n%s", df_merged[['scheduled_arrival', 'actual_arrival']].head())

    # Step 12: Save the merged dataset to CSV
    merged_data_path = os.path.join("outputs", "merged_train_station_data.csv")
    df_merged.to_csv(merged_data_path, index=False)
    logger.info("Merged data saved to %s", merged_data_path)

    return df_merged

# Now data is ready for uploading to PostgreSQL and turning into a map