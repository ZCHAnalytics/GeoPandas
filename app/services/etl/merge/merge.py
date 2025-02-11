# app/services/etl/merge/merge.py

import pandas as pd
from app.core.logging_config import configure_logging
from .station_matcher import StationMatcher
from .data_merger import DataMerger

logger = configure_logging()

def merge_geospatial_data(cleaned_delays: pd.DataFrame) -> pd.DataFrame:
    """
    Merge cleaned train arrival data with geospatial station data.
    
    Args:
        cleaned_delays: DataFrame containing cleaned train delay data
        
    Returns:
        DataFrame with merged geospatial coordinates
    """
    try:
        logger.info("🚀 Starting geospatial data merge process...")
        
        # Initialise merger and load data
        merger = DataMerger()
        df_delays, df_coords = merger.load_dataframes(cleaned_delays)
        
        # Initialise station matcher
        matcher = StationMatcher(set(df_coords["station_name"].unique()))
        
        # Apply name corrections
        logger.info("🔄 Applying station name corrections...")
        df_delays["origin"] = df_delays["origin"].apply(matcher.get_corrected_name)
        df_delays["destination"] = df_delays["destination"].apply(
            matcher.get_corrected_name
        )
        
        # Merge coordinates
        logger.info("🔄 Merging with coordinate data...")
        df_merged = merger.merge_coordinates(df_delays, df_coords)
        
        # Handle missing data
        logger.info("🧹 Handling missing data...")
        df_merged = merger.handle_missing_data(df_merged)
        
        # Save final merged data
        df_merged.to_csv('data/outputs/merged_train_station_data.csv', index=False)
        logger.info("✅ Successfully merged %d records", len(df_merged))
        
        return df_merged
        
    except Exception as e:
        logger.error("❌ Error in merge_geospatial_data: %s", str(e))
        raise