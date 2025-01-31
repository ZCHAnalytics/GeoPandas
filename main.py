# main.py

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager 

from db_main import engine, get_db
from db_schema import TrainTracking
from schema import TrainCreate # import pydantic schema 
from services.delays import get_delays_info
from services.plots import plot_delays_trends

origin = "FPK" # origin default
destination = "KGX" # destination default 

async def fetch_and_store_past_trains(origin: str, destination: str, db: AsyncSession):
    df = get_delays_info(origin, destination)
    if df.empty:
        print("No train data found. Skipping db update")
        return {"message": "No train data found"}
    print(df.head())
    all_trains =[]
    for train in df.to_dict(orient="records"):
        
        all_trains.append(TrainTracking(**train))

    db.add_all(all_trains)
    await db.commit()
    return {"message": f"Stored {len(all_trains)} train records in DB"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSession(engine) as db:
        await fetch_and_store_past_trains(origin, destination, db)
    yield

# Instantiate FastAPI app
app = FastAPI(lifespan=lifespan)

# Endpoint for delays info
@app.get("/api/delays")
def fetch_delays_info(origin:str = origin, destination: str = destination):
    df = get_delays_info(origin, destination)
    return df.to_dict(orient="records")
 
@app.get("/api/delays_chart")
def fetch_delays_chart(origin:str = origin, destination: str = destination):
    df = get_delays_info(origin, destination)
    return plot_delays_trends(df, origin, destination)

# New train record
@app.post("/api/trains/")
async def add_train(train: TrainCreate, db: AsyncSession = Depends(get_db)):
    new_train = TrainTracking(**train.model_dump())
    db.add(new_train)
    await db.commit()
    return {"message": "train record added"}

# get all train records
@app.get("/api/trains/")
async def get_trains(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrainTracking))
    return result.scalars().all()
