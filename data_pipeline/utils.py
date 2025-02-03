# utils.py - Load cleaned data into PostgreSQL

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_main import engine
from db.db_schema_alchemy import TrainTracking

async def upload_to_db(df_clean: pd.DataFrame):  
    """
    Upload cleaned train data from a DataFrame to PostgreSQL.
    
    Args:
        df_clean (pd.DataFrame): Cleaned train data.
    """
    if df_clean.empty:
        print("❌ No data to upload. DataFrame is empty.")
        return
    
    # ✅ Convert 'run_date' from string to datetime.date
    print("Converting run_date string to datetime.date type")
    df_clean["run_date"] = pd.to_datetime(df_clean["run_date"]).dt.date

    # ✅ Convert 'scheduled_arrival' and 'actual_arrival' to proper TIMESTAMP format
    df_clean["scheduled_arrival"] = pd.to_datetime(df_clean["run_date"].astype(str) + " " + df_clean["scheduled_arrival"])
    df_clean["actual_arrival"] = pd.to_datetime(df_clean["run_date"].astype(str) + " " + df_clean["actual_arrival"])

    async with AsyncSession(engine) as db:
        try:
            all_trains = [TrainTracking(**row) for row in df_clean.to_dict(orient="records")]
            db.add_all(all_trains)
            await db.commit()
            print("✅ Data successfully uploaded to PostgreSQL!")
        except Exception as e:
            print(f"❌ Database upload failed: {e}")
