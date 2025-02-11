# test_map_simple.py

import asyncio
from app.db.db_main import db_manager
from app.services.etl.mapping import generate_map
from app.services.etl.mapping.map_config import MapConfig

async def test_map():
    async with db_manager.SessionLocal() as session:
        print("Generating map...")
        map_path = await generate_map(db_manager, output_path)
        print(f"Map path: {map_path}")
        print(f"Map path type: {type(map_path)}")
        
        if map_path and isinstance(map_path, str):
            print("✅ Success!")
        else:
            print("❌ Failed!")

if __name__ == "__main__":
    asyncio.run(test_map())