# test file for plotting 
import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, Response
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import io
import base64
from test_df import get_delays_info  

load_dotenv()

USERNAME = os.getenv("RTT_USERNAME")
PASSWORD = os.getenv("RTT_PASSWORD")
ENDPOINT = os.getenv("RTT_ENDPOINT")

base_url=f"https://{ENDPOINT}/json/search/"
    
app = FastAPI()

# Endpoint for delays info chart 
@app.get("/api/delays_chart")
def plot_delays_trends(origin:str, destination: str):
    delay_data = get_delays_info(origin, destination)
    df = pd.DataFrame(delay_data) 

    if df.empty:
        return {"error": "No delay info retrieved"}
    df["date"] = pd.to_datetime(df["date"])

    delay_trends = df.groupby("date")["delay_minutes"].sum().reset_index()
    
    plt.figure(figsize=(10,5))
    plt.bar(delay_trends["date"], delay_trends["delay_minutes"], color="blue")
    plt.xlabel("Date")
    plt.ylabel("Total Delay Minutes")
    plt.title(f"Train Delays for {origin} to {destination}")
    plt.xticks(rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return Response(content=img.getvalue(), media_type="image/png")
