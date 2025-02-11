# setup.py

from setuptools import setup, find_packages

setup(
    name="train-tracking",  # Use hyphen instead of underscore for pip
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.7",
        "uvicorn>=0.34.0",
        "sqlalchemy[asyncio]>=2.0.37",
        "asyncpg>=0.30.0",
        "pandas>=2.0.1",
        "geopandas>=0.14.4",
        "folium>=0.19.4",
        "python-dotenv>=1.0.1",
        "pytest>=8.3.4",
        "pytest-asyncio>=0.25.3",
        "pytest-cov>=6.0.0",
        "httpx>=0.28.1",
        "GeoAlchemy2>=0.17.0",
        "fuzzywuzzy>=0.18.0",
        "alembic>=1.14.1"
    ],
)