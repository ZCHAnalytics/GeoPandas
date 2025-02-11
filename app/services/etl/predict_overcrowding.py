# app.... predict_overcrowding.py 

import pandas as pd
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.etl.map import TrainDelayMap
from app.core.logging_config import configure_logging

logger = configure_logging()

TABLE_NAME = "arrivals_tracking"

async def predict_crowding(db_session: AsyncSession):
    """
    Predicts station crowding based on real-time arrivals and historical delay patterns.

    Args:
        db_session (AsyncSession): Async database session to fetch records.

    Returns:
        pd.DataFrame: DataFrame containing predicted busy stations.
    """
    try: 
        # Instantiate the TrainDelayMap class 
        data_fetcher = TrainDelayMap()

        # Fetch delay data by calling the instance method
        delay_data = await data_fetcher.fetch_delay_data(db=db_session)

        if not delay_data:
            print("error")
            return pd.DataFrame()
        
        # Convert the delay data to df
        df = pd.DataFrame(delay_data)
        
        # Aggregate data to get arrival counts and average delay by station origin
        df_crowding = df.groupby('origin').agg(
            arrival_count=('service_id', 'count'),
            avg_delay=('delay_minutes', 'mean')
        ).reset_index()

        # Log the predicted overcrowding information
        logger.info(f"📊 Predicted crowding at busiest stations: {df_crowding.to_dict(orient='records')}")
        return df_crowding

    except Exception as e:
        logger.error(f"❌ Error predicting station crowding: {e}")
        return pd.DataFrame()
