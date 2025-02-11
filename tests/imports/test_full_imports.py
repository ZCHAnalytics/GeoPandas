# test_full_imports.py

import os
from pathlib import Path

print("Starting full import test...")

# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

try:
    print("\n1. Testing settings...")
    from app.core.config import settings
    print("✅ Settings imported")
    print(f"Database URL: {settings.database_url}")
    
    print("\n2. Testing database...")
    from app.db.db_main import db_manager, get_db, init_db
    print("✅ Database modules imported")
    print(f"Database Manager: {db_manager}")
    
    print("\n3. Testing ETL modules...")
    from app.services.etl.extract import extract_data
    print("✅ Extract module imported")
    from app.services.etl.clean import process_data
    print("✅ Clean module imported")
    from app.services.etl.merge import merge_geospatial_data
    print("✅ Merge module imported")
    from app.services.etl.map import generate_html_map
    print("✅ Map module imported")
    
    print("\n4. Testing API modules...")
    from app.api.endpoints.train_delays import router as train_delays_router
    print("✅ Train delays endpoint imported")
    
    print("\n5. Testing main application...")
    from app.main import app
    print("✅ Main application imported")

    print("\n✅ All imports successful!")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()