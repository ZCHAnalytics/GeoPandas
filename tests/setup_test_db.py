# scripts/setup_test_db.py

import asyncio
import asyncpg
from app.core.config import settings
from urllib.parse import urlparse

async def setup_test_db():
    """Set up test database with same schema as main database."""
    try:
        # Parse URLs
        main_url = urlparse(str(settings.database_url))
        test_url = urlparse(str(settings.test_database_url))
        
        print(f"Setting up test database: {test_url.path.lstrip('/')}")
        
        # Connect to test database
        test_conn = await asyncpg.connect(
            user=test_url.username,
            password=test_url.password,
            host=test_url.hostname,
            database=test_url.path.lstrip('/')
        )
        
        try:
            # Create PostGIS extension
            print("\n1. Setting up PostGIS...")
            await test_conn.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
            print("✅ PostGIS extension created")
            
            # Drop existing table and sequence if they exist
            print("\n2. Cleaning up existing objects...")
            await test_conn.execute("""
                DROP TABLE IF EXISTS test_trains CASCADE;
                DROP SEQUENCE IF EXISTS test_trains_id_seq;
            """)
            print("✅ Old objects dropped")
            
            # Create sequence
            print("\n3. Creating sequence...")
            await test_conn.execute("""
                CREATE SEQUENCE test_trains_id_seq
                    INCREMENT 1
                    START 1
                    MINVALUE 1
                    MAXVALUE 2147483647
                    CACHE 1;
            """)
            print("✅ Sequence created")
            # Definte table name as constant
            TABLE_NAME = "test_trains"

            # Create table
            print("\n4. Creating table...")
            await test_conn.execute(f"""
                CREATE TABLE {TABLE_NAME} (
                    id INTEGER NOT NULL DEFAULT nextval('test_trains_id_seq'::regclass),
                    run_date DATE NOT NULL,
                    service_id VARCHAR(10) NOT NULL,
                    operator VARCHAR(50) NOT NULL,
                    origin VARCHAR(50) NOT NULL,
                    origin_crs VARCHAR(6),
                    origin_latitude DOUBLE PRECISION,
                    origin_longitude DOUBLE PRECISION,
                    origin_geom geometry(Point, 4326),
                    destination VARCHAR(50) NOT NULL,
                    destination_crs VARCHAR(6),
                    destination_latitude DOUBLE PRECISION,
                    destination_longitude DOUBLE PRECISION,
                    destination_geom geometry(Point, 4326),
                    scheduled_arrival TIMESTAMP NOT NULL,
                    actual_arrival TIMESTAMP,
                    is_actual BOOLEAN,
                    delay_minutes INTEGER,
                    is_passenger_train BOOLEAN NOT NULL DEFAULT TRUE,
                    was_scheduled_to_stop BOOLEAN NOT NULL DEFAULT TRUE,
                    stop_status VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN',
                    CONSTRAINT {TABLE_NAME}_pkey PRIMARY KEY (id)
                );
            """)
            print("✅ Table created")
          
            # Add any indexes
            print("\n6. Creating indexes...")
            await test_conn.execute(f"""
                CREATE INDEX idx_{TABLE_NAME}_run_date ON {TABLE_NAME}(run_date);
                CREATE INDEX idx_{TABLE_NAME}_service_id ON {TABLE_NAME}(service_id);
                CREATE INDEX idx_{TABLE_NAME}_origin_geom ON {TABLE_NAME} USING GIST(origin_geom);
                CREATE INDEX idx_{TABLE_NAME}_destination_geom ON {TABLE_NAME} USING GIST(destination_geom);
            """)
            print("✅ Indexes created")
            
            print("\n✅ Test database setup complete!")
            
        finally:
            await test_conn.close()
            
    except Exception as e:
        print(f"\n❌ Error setting up test database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_test_db())