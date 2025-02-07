# utils.py - Load cleaned data into PostgreSQL

import pandas as pd
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Project modules 
from db.db_main import engine
from db.db_schema_alchemy import TrainTracking

# ✅  Set up logging for this module
logger = logging.getLogger(__name__)

                                               
async def upload_to_db(df_merged: pd.DataFrame):  
    """
    Upload cleaned train data from a DataFrame to PostgreSQL.
    
    Args:
        df_clean (pd.DataFrame): Cleaned train data.
    """
    if df_merged.empty:
        logger.error("❌ No data to upload. DataFrame is empty.")
        return
  
    # ✅  Adjust arrivals past mignight
    def adjust_date(row):
        """
        Adjusts the run_date if the next_day_arrival flag is True.
        Returns a datetime object.
        """
       # Use the non_adjusted_date as the base date, if there is a flag for next_day_arrival present (True), add one more day 
        base_date = pd.to_datetime(row["non_adjusted_date"])
        if row.get("next_day_arrival", True):
            return base_date + timedelta(days=1)
        return base_date

        
    # ✅ Convert 'scheduled_arrival' and 'actual_arrival' to proper TIMESTAMP format
    
    logger.info("Converting 'scheduled_arrival' and 'actual_arrival' to TIMESTAMP format.")

    df_merged["scheduled_arrival"] = pd.to_datetime(df_merged["run_date"].astype(str) + " " + df_merged["scheduled_arrival"])
    df_merged["actual_arrival"] = pd.to_datetime(df_merged["run_date"].astype(str) + " " + df_merged["actual_arrival"])

    async with AsyncSession(engine) as db:
        try:
            # Convert DataFrame records to a list of TrainTracking objects
            all_trains = [TrainTracking(**row) for row in df_merged.to_dict(orient="records")]
            db.add_all(all_trains)
            await db.commit()
            logger.info("✅ Data successfully uploaded to PostgreSQL!")
        except Exception as e:
            logger.error("❌ Database upload failed: %s", e)
            await db.rollback()
