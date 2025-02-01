# plots.py - Train Delay Visualisation 
 
from fastapi import APIRouter, Response
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg") # Prefvent issues in headless env
import io
import pandas as pd
from services.trains_delays import get_delays_info

# Create FastAPI Router instance 
router = APIRouter()

def plot_delays_trends(df, origin, destination):
    if df.empty:
        return {"error": "No delay data avaialbe"}
    
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"]) # Date column is in datetime format
    
    delay_trends = df.groupby("date")["delay_minutes"].sum().reset_index()
    
    plt.figure(figsize=(10,5))
    plt.bar(delay_trends["date"], delay_trends["delay_minutes"], color="blue", label="Delay Min")
    plt.xlabel("Date")
    plt.ylabel("Total Delay Min")
    plt.title(f"Train Delays for {origin} to {destination}")
    plt.xticks(delay_trends["date"][::2], rotation=45)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    # Convert plot to PNG response
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return Response(content=img.getvalue(), media_type="image/png")

# Define an API endpoint insider the router
@router.get("/api/delays_chart")
def fetch_delays_chart(origin: str = "FPK", destination: str = "KGX"):
    """
    API endpoint to generate a train delay trends chart.
    """
    df = get_delays_info(origin, destination)
    return plot_delays_trends(df, origin, destination)