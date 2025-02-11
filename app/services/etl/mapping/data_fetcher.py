# app/services/etl/mapping/data_fetcher.py

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.logging_config import configure_logging

logger = configure_logging()

async def fetch_delay_data(db: AsyncSession, hours: int = 24, cutoff_time: datetime = None, table_name: str = "test_trains") -> List[Dict[str, Any]]:
    """Fetch recent train delay data."""
    try:
        # Calculate the cutoff time
        if cutoff_time is None: 
            cutoff_time =  datetime.now() - timedelta(hours=hours)
        logger.info(f"cuttof time: {cutoff_time}")
        
        query = text(f"""
            SELECT 
                run_date,
                service_id,
                operator,
                origin,
                origin_crs,
                ST_X(origin_geom::geometry) as origin_longitude,
                ST_Y(origin_geom::geometry) as origin_latitude,
                destination,
                destination_crs,
                ST_X(destination_geom::geometry) as destination_longitude,
                ST_Y(destination_geom::geometry) as destination_latitude,
                scheduled_arrival,
                actual_arrival,
                delay_minutes,
                is_passenger_train
            FROM {table_name}
            WHERE scheduled_arrival >= :cutoff_time
              AND is_passenger_train = TRUE
            ORDER BY scheduled_arrival DESC
        """)
        
        result = await db.execute(query, {"cutoff_time": cutoff_time})
        rows = result.fetchall()
        
        logger.info(f"✅ Fetched {len(rows)} records from database")
        
        # Convert rows to dictionaries using _mapping
        data = [dict(row._mapping) for row in rows]
        logger.info(f"✅ Converted {len(data)} records to dictionaries")
    
        return data
            
    except Exception as e:
        logger.error(f"❌ Error fetching delay data: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise