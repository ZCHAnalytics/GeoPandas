# scripts/verify_schema.py

import asyncio
import sys
import asyncpg
from app.core.config import settings
from app.core.logging_config import setup_logging
from urllib.parse import urlparse

logger = setup_logging()

async def verify_database(is_test: bool = False):
    """Verify database schema."""
    try:
        # Parse database URL
        db_url = urlparse(str(settings.test_database_url if is_test else settings.database_url))
        
        # Extract connection details
        db_params = {
            'user': db_url.username,
            'password': db_url.password,
            'host': db_url.hostname,
            'database': db_url.path.lstrip('/')
        }

        # Connect to database
        conn = await asyncpg.connect(**db_params)
        
        try:
            # Check table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'arrivals_tracking'
                ORDER BY ordinal_position;
            """)
            
            print(f"\nTable structure for arrivals_tracking in {db_url.path.lstrip('/')}:")
            print("-" * 80)
            print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default':<20}")
            print("-" * 80)
            
            if not columns:
                print("❌ No columns found! Table might not exist.")
                return
                
            for col in columns:
                print(f"{col['column_name']:<30} {col['data_type']:<20} "
                      f"{col['is_nullable']:<10} {str(col['column_default'] or ''):<20}")

            # Check PostGIS extension
            postgis_version = await conn.fetchval("SELECT PostGIS_Version();")
            print(f"\nPostGIS Version: {postgis_version}")

            # Check spatial columns
            spatial_info = await conn.fetch("""
                SELECT
                    column_name,
                    udt_name,
                    ST_GeometryType(column_name::regclass::text::geometry) as geom_type,
                    ST_SRID(column_name::regclass::text::geometry) as srid
                FROM information_schema.columns
                WHERE table_name = 'arrivals_tracking'
                AND udt_name = 'geomatry';
            """)
            
            if spatial_info:
                print("\nSpatial Columns Details:")
                print("-" * 80)
                print(f"{'Column':<20} {'Type':<15} {'Geometry Type':<15} {'SRID':<8}")
                print("-" * 80)
                for col in spatial_info:
                    print(f"{col['column_name']:<20} {col['udt_name']:<15} "
                          f"{col['geom_type']:<15} {col['srid']:<8}")
            # Check if PostGIS geometry columns are properly registered
            print("\nChecking PostGIS registration...")
            registered_geom = await conn.fetch("""
                  SELECT f_geometry_column, type, srid, coord_dimension
                  FROM geometry_columns
                  WHERE f_table_name = 'arrivals_tracking';
            """)

            if not registered_geom:
                print("⚠️ Geometries not registered in geometry_columns. Adding them...")
                # Register the geometry columns
                await conn.execute("""
                    SELECT Populate_Geometry_Columns('arrivals_tracking'::regclass);
                """)
                print("✅ Geometry columns registered!")

            # Check record count
            count = await conn.fetchval("SELECT COUNT(*) FROM arrivals_tracking")
            print(f"\nTotal records: {count}")

            print("\n✅ Schema verification complete!")

        finally:
            # Close connection
            await conn.close()

    except Exception as e:
        logger.error(f"❌ Error verifying schema: {str(e)}")
        raise

async def main():
    """Main async function."""
    try:
        if args.test:
            print("\nVerifying TEST database...")
            await verify_database(is_test=True)
        else:
            print("\nVerifying MAIN database...")
            await verify_database(is_test=False)
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Verify database schema')
    parser.add_argument('--test', action='store_true', help='Verify test database')
    args = parser.parse_args()
    
    # Fix for Windows event loop policy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")