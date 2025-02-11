# test_settings.py
print("Starting settings test...")

try:
    print("1. Importing BaseSettings...")
    from pydantic_settings import BaseSettings
    print("✅ BaseSettings imported")

    print("\n2. Importing PostgresDsn...")
    from pydantic import PostgresDsn
    print("✅ PostgresDsn imported")

    print("\n3. Importing settings...")
    from app.core.config import settings
    print("✅ Settings imported")

    print("\n4. Checking settings values...")
    print(f"Database URL: {settings.database_url}")
    print(f"RTT Endpoint: {settings.RTT_ENDPOINT}")
    print(f"Base URL: {settings.base_url}")

    print("\n✅ All settings tests passed!")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()