# app/api/endpoints/__init__.py

from app.api.endpoints.train_delays import router as train_delays_router
from app.api.endpoints.busiest_stations import router as busiest_stations_router

__all__ = ['train_delays_router', 'busiest_stations_router']