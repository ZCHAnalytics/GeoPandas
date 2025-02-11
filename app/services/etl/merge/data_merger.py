# app/services/etl/merge/data_merger.py
import os
import pandas as pd
from typing import Tuple
from app.core.logging_config import configure_logging

logger = configure_logging()

class DataMerger:
    """Handles merging of train data with geospatial coordinates."""

    def load_dataframes(self, cleaned_delays: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load coordinates data and return with cleaned delays."""
        try:
            # Load coordinates data
            df_coords = pd.read_csv('data/geospatial/station_coordinates.csv')
            logger.info("✅ Successfully loaded coordinates data")
            logger.info(f"Delays data shape: {cleaned_delays.shape}")
            logger.info(f"Coordinates data shape: {df_coords.shape}")
            
            return cleaned_delays, df_coords
            
        except Exception as e:
            logger.error("❌ Error loading data: %s", str(e))
            raise

    def merge_coordinates(self, df_delays: pd.DataFrame, 
                         df_coords: pd.DataFrame) -> pd.DataFrame:
        """Merge delays data with coordinates."""
        # Merge with origin coordinates
        df_merged = pd.merge(
            df_delays, 
            df_coords,
            left_on="origin",
            right_on="station_name",
            how="left",
            suffixes=("", "_origin")
        )
        
        # Rename origin columns
        df_merged.rename(columns={
            "crs": "origin_crs",
            "latitude": "origin_latitude",
            "longitude": "origin_longitude"
        }, inplace=True)
        
        # Merge with destination coordinates
        df_merged = pd.merge(
            df_merged,
            df_coords,
            left_on="destination",
            right_on="station_name",
            how="left",
            suffixes=("", "_dest")
        )
        
        # Rename destination columns
        df_merged.rename(columns={
            "crs": "destination_crs",
            "latitude": "destination_latitude",
            "longitude": "destination_longitude"
        }, inplace=True)
        
        # Clean up redundant columns
        df_merged.drop(columns=["station_name", "station_name_dest"], inplace=True)
        
        return df_merged

    def handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing CRS values and log dropped records."""
        # Log missing CRS values
        missing_origin = df[df['origin_crs'].isna()]['origin'].value_counts()
        missing_dest = df[df['destination_crs'].isna()]['destination'].value_counts()
        
        if not missing_origin.empty:
            logger.warning("⚠️ Stations with missing origin CRS:\n%s", missing_origin)
        if not missing_dest.empty:
            logger.warning("⚠️ Stations with missing destination CRS:\n%s", missing_dest)
        
        # Save dropped records
        missing_records = df[df['origin_crs'].isna() | df['destination_crs'].isna()]
        if not missing_records.empty:
            missing_records.to_csv(
                'data/outputs/dropped_records.csv',
                mode='a',
                header=not os.path.exists('data/outputs/dropped_records.csv'),
                index=False
            )
            logger.info("📝 Saved %d dropped records", len(missing_records))
        
        # Drop records with missing CRS
        df_clean = df.dropna(subset=['origin_crs', 'destination_crs'])
        logger.info(f"Dropped {len(df) - len(df_clean)} records with missing CRS values")
        
        return df_clean