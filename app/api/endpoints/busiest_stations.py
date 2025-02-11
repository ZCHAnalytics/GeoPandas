# app/api/endpoints/busiest_stations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func

# Project Modules
from app.db.db_main import get_db
from app.services.etl.predict_overcrowding import predict_crowding
from app.core.logging_config import configure_logging

logger = configure_logging()

TABLE_NAME = "arrivals_tracking" 

router = APIRouter()

@router.get("/busiest-stations")

@router.get("/busiest_stations", tags=["Crowding Prediction"])
async def get_busiest_stations(db_session: AsyncSession = Depends(get_db)):
    """Returns predicted busiest stations based on real-time train arrivals."""
    crowding_df = await predict_crowding(db_session)
    return crowding_df.to_dict(orient="records")
