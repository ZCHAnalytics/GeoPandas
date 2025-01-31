# db_init.py

from db_main import engine
from db_schema import Base
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Optional: Clears existing tables
        await conn.run_sync(Base.metadata.create_all)  # Creates new tables
    print("Database and tables created!")

if __name__ == "__main__":
    if asyncio.get_event_loop_policy().__class__.__name__ == "WindowsProactorEventLoopPolicy":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(init_db())