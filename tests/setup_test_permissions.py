# scripts/setup_test_permissions.py
import asyncio
import asyncpg
from app.core.config import settings
from urllib.parse import urlparse
import os
from getpass import getpass

async def setup_permissions():
    """Set up necessary database permissions."""
    try:
        # Parse database URL
        db_url = urlparse(str(settings.test_database_url))
        target_user = db_url.username  # The user that needs permissions
        
        # Get postgres password securely
        postgres_password = getpass("Enter postgres user password: ")
        
        print("Connecting as superuser...")
        conn = await asyncpg.connect(
            user='postgres',
            password=postgres_password,
            database=db_url.path.lstrip('/'),  # test database name
            host=db_url.hostname
        )
        
        # Grant permissions
        print("\nSetting up permissions...")
        permissions_queries = [
            f"GRANT ALL ON SCHEMA public TO {target_user};",
            f"GRANT ALL ON ALL TABLES IN SCHEMA public TO {target_user};",
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {target_user};"
        ]
        
        for query in permissions_queries:
            try:
                await conn.execute(query)
                print(f"✅ Executed: {query}")
            except Exception as e:
                print(f"⚠️ Error executing {query}: {str(e)}")
        
        await conn.close()
        print("✅ Permissions setup completed!")
        
    except asyncpg.InvalidPasswordError:
        print("❌ Invalid postgres password!")
        print("Please make sure you have the correct postgres password")
    except Exception as e:
        print(f"❌ Error setting up permissions: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(setup_permissions())
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")