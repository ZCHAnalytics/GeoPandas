# tests/services/etl/mapping/test_integration.py

import pytest
import os
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app 

from app.services.etl.mapping.map_generator import generate_map
from app.services.etl.mapping.map_config import MapConfig
from app.services.etl.mapping.data_fetcher import fetch_delay_data
from app.core.logging_config import setup_logging

logger = setup_logging()

@pytest.fixture 
def test_client():
    with TestClient(app) as client: # use a content manager for proper cleanup 
        yield client

@pytest.mark.asyncio
async def test_integration(test_client, db):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Construct the output path using os.path.join and MapConfig.OUTPUT_DIR
    output_path = os.path.join(MapConfig.OUTPUT_DIR, f"train_delays_map_{timestamp}.html")

    print(f"Generated output path: {output_path}")

    # 1. Insert data before map generation 
    try: 
        def fetch_delay_data():
            now = datetime.now()
            logger.info(f"🛠️ Inserting test data for {now}")           
   
    except Exception as e:
        print(f"Error inserting test data: {e}")
        pytest.fail(f"Test data insertion failed: {e}")    
    
    # 2. Ensure the directory exists (important!)
    os.makedirs(MapConfig.OUTPUT_DIR, exist_ok=True)  
    
    # 3. Call map generation function 
    try: 
        await generate_map(db, output_path) # Pass the path and sessions
        print("Map generation successful.")
    except Exception as e:
        print(f"Error durng map generation: {e}")
        pytest.fail(f"Map generation failed: {e}")
    
    # 4. Assertions 
    assert os.path.exists(output_path), f"Map file not found at {output_path}"
    
    # check file content and close after reading 
    with open(output_path, 'r') as f:
        map_content = f.read()
 
    assert 'Kings Cross' in map_content, "Map should contain origin station"
    assert 'Finsbury Park' in map_content, "Map should contain destination station"
    assert 'leaflet' in map_content.lower(), "Map should be a Leaflet map"

    logger.info("✅ Map verification completed successfully")