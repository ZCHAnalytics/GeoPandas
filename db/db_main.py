# db_main.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

DATABASE_URL =os.getenv("DATABASE_URL")

# db async engine
engine = create_async_engine(DATABASE_URL, future=True)

# Session factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Dependency for FastAPI route
async def get_db():
    async with SessionLocal() as session:
        yield session