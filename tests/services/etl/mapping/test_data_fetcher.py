# tests/services/etl/mapping/test_data_fetcher.py

import pytest
from datetime import datetime, timedelta
from sqlalchemy import text, func
from app.services.etl.mapping.data_fetcher import fetch_delay_data
from app.core.logging_config import setup_logging

logger = setup_logging()

@pytest.mark.asyncio
async def test_fetch_delay_data(db, table_name: str = "test_trains"):
    """Test fetching delay data."""
            
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(hours=24)
    logger.info(f"🔍 Cutoff time for query: {cutoff_time}")


    # Prepare test data
    now = datetime.now()
    test_data = {
        "run_date": now.date(),
        "service_id": 'TEST001',
        "operator": 'TEST',
        "origin": 'Kings Cross',
        "origin_crs": 'KGX',
        "origin_latitude": 51.5320,
        "origin_longitude": -0.1240,
        "destination": 'Finsbury Park',
        "destination_crs": 'FPK',
        "destination_latitude": 51.5643,
        "destination_longitude": -0.1063,
        "scheduled_arrival": now,
        "actual_arrival": now + timedelta(minutes=10),
        "delay_minutes": 10,
        "is_passenger_train": True,
        "was_scheduled_to_stop": True,
        "stop_status": 'NORMAL'
    }

    # Insert test data

    await db.execute(
        text(f"""
            INSERT INTO {table_name} (
                run_date, service_id, operator, 
                origin, origin_crs, origin_latitude, origin_longitude, origin_geom,
                destination, destination_crs, destination_latitude, destination_longitude, destination_geom,
                scheduled_arrival, actual_arrival, delay_minutes, 
                is_passenger_train, was_scheduled_to_stop, stop_status 
            ) VALUES (
                :run_date, :service_id, :operator,
                :origin, :origin_crs, :origin_latitude, :origin_longitude,
                ST_SetSRID(ST_MakePoint(:origin_longitude, :origin_latitude), 4326),
                :destination, :destination_crs, :destination_latitude, :destination_longitude, 
                ST_SetSRID(ST_MakePoint(:destination_longitude, :destination_latitude), 4326),
                :scheduled_arrival, :actual_arrival, :delay_minutes,
                :is_passenger_train, :was_scheduled_to_stop, :stop_status
                
            )
        """),
        test_data
    )
    print(f"Test record scheduled arrival: {test_data['scheduled_arrival']} at run date {test_data['run_date']}")

    await db.commit()
    print("transaction committed to the test_trains table")

    # Fetch data using the cutoff_time
    delay_data = await fetch_delay_data(db, cutoff_time=cutoff_time)
    
    # Verify results
    assert len(delay_data) > 0, "Should have at least one record"
    record = delay_data[0]
    assert record['service_id'] == 'TEST001', "Should match test service ID"
    assert record['origin'] == 'Kings Cross', "Should match test origin"
    assert record['destination'] == 'Finsbury Park', "Should match test destination"

