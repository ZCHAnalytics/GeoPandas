# app/api/endpoints/train_delays.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.db.db_main import get_db
from app.services.etl.map import TrainDelayMap
from app.services.etl.mapping.data_fetcher import fetch_delay_data

from app.core.logging_config import setup_logging

logger = setup_logging()

router = APIRouter()

async def predict_station_busyness(
    db: AsyncSession,
    station: str,
    look_ahead_hours: int = 1
) -> Dict[str, Any]:
    """
    Predicts station busyness based on scheduled arrivals and current delays.
    
    Args:
        db: Database session
        station: Station CRS code
        look_ahead_hours: Hours to look ahead for prediction
        
    Returns:
        Dictionary containing prediction details
    """
    try:
        # Fetch scheduled arrivals
        query = """
            WITH upcoming_arrivals AS (
                SELECT 
                    destination_crs,
                    scheduled_arrival,
                    delay_minutes,
                    COUNT(*) as train_count,
                    AVG(delay_minutes) as avg_delay
                FROM arrivals_tracking
                WHERE destination_crs = :station
                AND scheduled_arrival BETWEEN NOW() 
                    AND NOW() + INTERVAL :hours HOUR
                GROUP BY destination_crs, scheduled_arrival, delay_minutes
            )
            SELECT 
                COUNT(*) as total_trains,
                AVG(train_count) as avg_trains_per_hour,
                AVG(CASE WHEN delay_minutes > 10 THEN 1 ELSE 0 END) as delayed_ratio,
                AVG(avg_delay) as average_delay
            FROM upcoming_arrivals;
        """
        
        result = await db.execute(
            text(query),
            {"station": station, "hours": look_ahead_hours}
        )
        stats = dict(result.fetchone())
        
        # Calculate busyness score (example algorithm)
        busyness_score = (
            stats['avg_trains_per_hour'] * 
            (1 + stats['delayed_ratio']) * 
            (1 + stats['average_delay']/60)
        )
        
        return {
            "station": station,
            "prediction_window": f"Next {look_ahead_hours} hour(s)",
            "expected_trains": stats['total_trains'],
            "average_delay": stats['average_delay'],
            "busyness_score": busyness_score,
            "busyness_level": "High" if busyness_score > 7 
                            else "Medium" if busyness_score > 4 
                            else "Low"
        }
        
    except Exception as e:
        logger.error("Failed to predict station busyness: %s", str(e))
        raise

@router.get("/train_delays_map", response_class=HTMLResponse, tags=["Train Delays"])
async def get_train_delays_map(
    db: AsyncSession = Depends(get_db),
    hours: int = Query(1, ge=1, le=24),
    station: Optional[str] = Query(None, max_length=3)
):
    """
    Generates an HTML map showing train delays.
    
    Args:
        db: Database session
        hours: Hours of historical data to show
        station: Optional station filter
    """
    try:
        # Fetch data from PostGIS
        delay_data = await fetch_delay_data(db, hours, station)
        
        if not delay_data:
            return HTMLResponse(
                content="<h2>No train data available for the specified criteria</h2>",
                status_code=404)
        """
        Generates a map using TrainDelayMap .
        """
        map_generator = TrainDelayMap()
        map_html_path = await map_generator.generate_map(db, hours) 
            
        # Read generated HTML
        with open(map_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        logger.error(f"Failed to generate map: {e}")
        return HTMLResponse(content="<h2>Internal Server Error</h2>",
            status_code=500
        )

@router.get("/station_busyness/{station}", tags=["Station Predictions"])
async def get_station_busyness(
    station: str,
    db: AsyncSession = Depends(get_db),
    look_ahead_hours: int = Query(1, ge=1, le=24)
):
    """
    Predicts station busyness for the specified time window.
    
    Args:
        station: Station CRS code
        db: Database session
        look_ahead_hours: Hours to look ahead for prediction
    """
    try:
        prediction = await predict_station_busyness(
            db, 
            station.upper(), 
            look_ahead_hours
        )
        return JSONResponse(content=prediction)
        
    except Exception as e:
        logger.error("Error predicting station busyness: %s", str(e))
        return JSONResponse(
            content={"error": "Failed to predict station busyness"},
            status_code=500
        )

@router.get("/station_status/{station}", tags=["Station Status"])
async def get_station_status(
    station: str,
    db: AsyncSession = Depends(get_db),
    hours: int = Query(1, ge=1, le=24)
):
    """
    Gets current station status including delays and predictions.
    
    Args:
        station: Station CRS code
        db: Database session
        hours: Hours of historical data to include
    """
    try:
        # Fetch both current delays and future predictions
        delay_data = await fetch_delay_data(db, hours, station.upper())
        prediction = await predict_station_busyness(db, station.upper())
        
        current_status = {
            "station": station.upper(),
            "current_delays": delay_data,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=current_status)
        
    except Exception as e:
        logger.error("Error fetching station status: %s", str(e))
        return JSONResponse(
            content={"error": "Failed to fetch station status"},
            status_code=500
        )