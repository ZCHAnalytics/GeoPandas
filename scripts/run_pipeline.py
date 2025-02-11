# app/services/etl/run_pipeline.py
import asyncio
from datetime import datetime 
from sqlalchemy.ext.asyncio import AsyncSession

# Project modules
from app.core.logging_config import configure_logging
from app.services.etl.extract import extract_and_save_arrivals_data
from app.services.etl.clean import process_data
from app.services.etl.merge import merge_geospatial_data
from app.crud.train_crud import upload_to_db
from app.services.etl.map import TrainDelayMap
from app.db.db_main import get_db, close_database_connections
from app.services.etl.predict_overcrowding import predict_crowding

logger = configure_logging()


async def run_data_pipeline(station: str, days: int):
    """
    Runs the complete ETL pipeline: Extract, Clean, Merge, Upload, Map Generation. and Crowding Prediction.
    
    Args:
        station (str): Station code to extract data for.
        days (int): Number of past days to extract data.
    """
    today_date = datetime.today().strftime('%Y-%m-%d')  # Ensures it's a string, not a datetime object
        
    logger.info("🛢️ Running data pipeline for station '%s' over the past %d days.", station, days)
    
    # USE CONTEXT MANAGER TO MANAGE DB SESSION 
    async with get_db() as db_session:
        raw_data = None
        df_clean = None
        df_merged = None 
        
        try: 
            # STEP 1: EXTRACT LIVE ARRIVALS DATA 
            logger.info("🔍 Extracting live data...")
        
            # Ensure that the date is properly formatted as a string in 'YYYY-MM-DD' format
            raw_data = await extract_and_save_arrivals_data(station, days)
            
            if not raw_data or "services" not in raw_data:
                logger.error("❌ No valid raw data found. Halting pipeline.", today_date)
                return
    

            # STEP 2: PROCESS AND ClEAN 
            logger.info("🛠️ Processing and cleaning extracted data...")
            df_clean = process_data(raw_data)
            if  df_clean is None or df_clean.empty:
                logger.error("❌ No valid train records after processing. Halting pipeline.")
                return
            

            # STEP 3: MERGE WITH COORDINATES
            logger.info("🔗 Merging with geospatial data...")
            df_merged = merge_geospatial_data(df_clean)
            if df_merged.empty or df_merged is None:
                logger.error("❌ No valid train records after merging geospatial data. Halting pipeline.")
                return
            

            # STEP 4: LOAD TO DATABASE 
            logger.info("💾 Uploading cleaned data to the database...")
            await upload_to_db(df_merged, db_session)
            if db_session is not None:
                await db_session.commit()
            

            # STEP 5: GENERATE HTML MAP 
            logger.info("🗺️ Generating HTML map...")
            map_generator = TrainDelayMap()
            map_path = await map_generator.generate_map(db_session)
            
            if map_path:
                logger.info("✅ Map successfully generated at '%s'.", map_path)
            else:
                logger.warning("⚠️ Map generation returned no map path.")
            
            
            # STEP 6: Predict station crowding
            logger.info("📊 Predicting station crowding...")
            crowding_df = await predict_crowding(db_session)
            
            if not crowding_df.empty:
                logger.info("✅ Crowding prediction complete.")
            else:
                logger.warning("⚠️ No significant crowding detected.")

        except Exception as e:
            logger.error(f"❌ An error occurred during the pipeline: {e}")
            await db_session.rollback() 
            raise 

    logger.info("🏁 ETL  pipeline completed successfully.")

async def main ():
    station = "FPK"
    days = 7
    
    await run_data_pipeline(station, days)
    await close_database_connections()

if __name__ == "__main__":
    asyncio.run(main())  # Ensures async functions are properly executed