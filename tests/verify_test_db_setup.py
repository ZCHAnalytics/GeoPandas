# scripts/verify_test_db_setup.py

import asyncio
import asyncpg
from app.core.config import settings
from typing import List
from urllib.parse import urlparse

async def verify_setup():
    """Verify database setup and permissions."""
    try:
        # Parse the database URL
        db_url = urlparse(str(settings.test_database_url))
        
        # Extract components
        user = db_url.username
        password = db_url.password
        host = db_url.hostname
        database = db_url.path.lstrip('/')
        
        # Connect as trains_user
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            database=database
        )
        
        # List of verifications to perform
        checks: List[str] = [
            # Check if we can create a table
            """
            CREATE TABLE IF NOT EXISTS test_permissions (
                id serial PRIMARY KEY,
                name text
            )
            """,
            
            # Check if we can insert data
            """
            INSERT INTO test_permissions (name) 
            VALUES ('test_record')
            """,
            
            # Check if we can query data
            """
            SELECT * FROM test_permissions
            """,
            
            # Check PostGIS
            """
            SELECT PostGIS_Version()
            """,
            
            # Clean up
            """
            DROP TABLE test_permissions
            """
        ]
        
        print("Running permission checks...")
        for i, check in enumerate(checks, 1):
            try:
                await conn.execute(check)
                print(f"✅ Check {i} passed: {check.strip().split()[0]}")
            except Exception as e:
                print(f"❌ Check {i} failed: {str(e)}")
                raise
        
        print("\n✅ All permission checks passed!")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Setup verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(verify_setup())