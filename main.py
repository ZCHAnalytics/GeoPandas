# main.py

from fastapi import FastAPI
from services.delays import get_delays_info
from services.plots import plot_delays_trends
    
# Instantiate FastAPI app
app = FastAPI()

# Endpoint for delays info
@app.get("/api/delays")
def fetch_delays_info(origin:str, destination: str):
    df = get_delays_info(origin, destination)
    return df.to_dict(orient="records")
 
@app.get("/api/delays_chart")
def fetch_delays_chart(origin:str, destination: str):
    df = get_delays_info(origin, destination)
    return plot_delays_trends(df, origin, destination)