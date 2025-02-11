# app/crud/train_crud.py
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from app.core.logging_config import configure_logging

logger = configure_logging()
TABLE_NAME = "arrivals_tracking"

async def upload_to_db(df_merged: pd.DataFrame, db_seession: AsyncSession) -> Optional[Exception]:
    """
    Upload cleaned train data to PostgreSQL, including PostGIS geometry fields.

    Args:
        df_merged (pd.DataFrame): Cleaned train data with latitude and longitude values.
        db_session (AsynceSession): The asyncronouc database session to use.

    Returns:
        Optional[Exception]: Returns an exception instance if upload fails, otherwise None.
    """
    if df_merged.empty:
        logger.error("❌ No data to upload. DataFrame is empty.")
        return None  # Early exit without raising an exception

    try:
        # Convert 'scheduled_arrival' and 'actual_arrival' to proper TIMESTAMP format
        logger.info("🔄 Converting 'scheduled_arrival' and 'actual_arrival' to TIMESTAMP format.")
        df_merged["scheduled_arrival"] = pd.to_datetime(
            df_merged["run_date"].astype(str) + " " + df_merged["scheduled_arrival"],
            errors='coerce'  # Converts invalid parsing to NaT
        )
        df_merged["actual_arrival"] = pd.to_datetime(
            df_merged["run_date"].astype(str) + " " + df_merged["actual_arrival"],
            errors='coerce'
        )

        # Optional: Drop rows with invalid datetime conversions
        initial_count = len(df_merged)
        df_merged.dropna(subset=["scheduled_arrival", "actual_arrival"], inplace=True)
        final_count = len(df_merged)
        if final_count < initial_count:
            logger.warning(f"⚠️ Dropped {initial_count - final_count} records due to invalid datetime conversions.")

        async with db_seession.begin():
            # Define the SQL statement with PostGIS geometry
            insert_sql = text(f"""
                INSERT INTO {TABLE_NAME} 
                (
                    run_date, service_id, operator, origin, origin_crs, origin_latitude, origin_longitude, origin_geom, 
                    destination, destination_crs, destination_latitude, destination_longitude, destination_geom, 
                    scheduled_arrival, actual_arrival, is_actual, delay_minutes, is_passenger_train, 
                    was_scheduled_to_stop, stop_status
                )
                VALUES 
                (
                    :run_date, :service_id, :operator, :origin, :origin_crs, :origin_latitude, :origin_longitude, 
                    ST_SetSRID(ST_MakePoint(:origin_longitude, :origin_latitude), 4326),
                    :destination, :destination_crs, :destination_latitude, :destination_longitude, 
                    ST_SetSRID(ST_MakePoint(:destination_longitude, :destination_latitude), 4326),
                    :scheduled_arrival, :actual_arrival, :is_actual, :delay_minutes, :is_passenger_train, 
                    :was_scheduled_to_stop, :stop_status
                )
            """)

            # Convert DataFrame to list of dictionaries
            records = df_merged.to_dict(orient="records")
            logger.info(f"🔢 Preparing to upload {len(records)} records to PostgreSQL.")

            # Bulk insert records
            await db_seession.execute(insert_sql, records)
            
            logger.info("✅ Data successfully uploaded to PostgreSQL with PostGIS!")

    except Exception as e:
        logger.error("❌ Database upload failed: %s", e)
        try:
            await db_session.rollback()
            logger.info("🔄 Rolled back the transaction due to the error.")
        except Exception as rollback_error:
            logger.error("❌ Failed to rollback the transaction: %s", rollback_error)
        return e  # Return the exception for upstream handling

    return None  # Indicate success