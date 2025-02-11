# FastAPI Train API + Data Pipeline (Extract → Clean → Upload)
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.logging_config import configure_logging
from app.core.config import settings

# Project modules for the data pipeline
from app.api.endpoints.train_delays import router as train_delays_router
from app.api.endpoints.busiest_stations import router as busiest_stations_router 

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_main import get_db 

# Set up logging 
logger = configure_logging()

# Initialise FastAPI app
app = FastAPI(
    title="Train Delays API",
    description="API for tracking and visualising train delays.",
    version="1.0.0",
)

# Include Routers
app.include_router(train_delays_router, prefix="/trains-delays", tags=["Train Delays"])
app.include_router(
    busiest_stations_router, 
    prefix="/predictions", 
    tags=["Station Predictions"]
)


# ✅ Run FastAPI server (if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)