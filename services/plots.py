# plots.py 
 
from fastapi import Response
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import io
import pandas as pd


def plot_delays_trends(df, origin, destination):
    if df.empty:
        return {"error": "No delay data avaialbe"}
    
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"]) 
    delay_trends = df.groupby("date")["delay_minutes"].sum().reset_index()
    
    plt.figure(figsize=(10,5))
    plt.bar(delay_trends["date"], delay_trends["delay_minutes"], color="blue", label="Delay Min")
    plt.xlabel("Date")
    plt.ylabel("Total Delay Min")
    plt.title(f"Train Delays for {origin} to {destination}")
    plt.xticks(delay_trends["date"][::2], rotation=45)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return Response(content=img.getvalue(), media_type="image/png")
