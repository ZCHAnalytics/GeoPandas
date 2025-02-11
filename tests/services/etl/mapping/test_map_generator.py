# tests/services/etl/mapping/test_map_generator.py
import os
from datetime import datetime
import pytest
from app.services.etl.mapping.map_generator import generate_map

@pytest.fixture
def sample_delay_data():
    """Provide sample delay data for testing."""
    return [{
        'run_date': datetime.now().date(),
        'service_id': 'TEST001',
        'operator': 'TEST',
        'origin': 'Kings Cross',
        'origin_crs': 'KGX',
        'origin_latitude': 51.5320,
        'origin_longitude': -0.1240,
        'destination': 'Finsbury Park',
        'destination_crs': 'FPK',
        'destination_latitude': 51.5643,
        'destination_longitude': -0.1063,
        'scheduled_arrival': datetime.now(),
        'actual_arrival': datetime.now(),
        'delay_minutes': 10,
        'is_passenger_train': True
    }]

@pytest.mark.asyncio
async def test_map_generator(sample_delay_data, db):
    """Test map generation functionality."""

    output_path = os.path.join("tests", "data", "maps", "test_map.html")
    map_path = await generate_map(db, output_path)

    try:

        # Test marker color logic
        assert map_path is not None 
        assert map_path.endwith('.html')
        assert os.path.exists(map_path)
    

    finally:
        # Clean up the test map file
        if os.path.exists(map_path):
            os.remove(map_path)
    