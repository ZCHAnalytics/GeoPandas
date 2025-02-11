# app/services/etl/mapping/map_generator.py
import asyncio
import folium
from folium import Element
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import configure_logging
from app.services.etl.mapping.data_fetcher import fetch_delay_data
from app.services.etl.mapping.map_config import MapConfig
from app.db.db_main import db_manager

logger = configure_logging()

# Helper functions (defined outside of async function) 
    
def _get_marker_color(delay: int) -> str:
    """Determines marker color based on delay severity."""
    if delay < 0:
        return "green"  # Early
    elif delay > 10:
        return "red"    # Significant delay
    else:
        return "orange" # Minor delay or on time

def _create_popup_content(record: Dict[str, Any]) -> str: # Inner helper
    """Creates HTML content for marker popups."""
    return f"""
        <b>Origin:</b> {record.get('origin')} (CRS: {record.get('origin_crs')})<br>
        <b>Destination:</b> {record.get('destination')} (CRS: {record.get('destination_crs')})<br>
        <b>Scheduled:</b> {record.get('scheduled_arrival')}<br>
        <b>Delay:</b> {record.get('delay_minutes')} minutes
    """

def _add_legend(map_obj: folium.Map) -> None:
    """Adds a legend to the map."""
    legend_html = """
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; 
                    border:2px solid grey; z-index:9999; 
                    background-color:white; padding: 10px;
                    font-size:12px;">
            <p><i class="fa fa-circle" style="color:green"></i> Early</p>
            <p><i class="fa fa-circle" style="color:orange"></i> On Time</p>
            <p><i class="fa fa-circle" style="color:red"></i> Delayed</p>
            <p><i class="fa fa-flag" style="color:blue"></i> Destination</p>
        </div>
    """
    map_obj.get_root().html.add_child(Element(legend_html))


async def generate_map_async(db, output_path: str): # Async inner function 
    try:
        trains = await fetch_delay_data(db) 

        if not trains:
            print("No trains data to generate map")
            return
        
        # Use MapConfig instead of hardcorded values 
        FPK_LATITUDE = MapConfig.FPK_LATITUDE
        FPK_LONGITUDE = MapConfig.FPK_LONGITUDE

        
        # Create base map
        m = folium.Map(
            location=[FPK_LATITUDE, FPK_LONGITUDE],
            zoom_start=10
        )
        
        # Add markers for each train service
        for record in trains:
            try:
                # Skip if missing coordinates
                if not all([
                    record.get('origin_latitude'), 
                    record.get('origin_longitude'),
                    record.get('destination_latitude'), 
                    record.get('destination_longitude')
                ]):
                    logger.warning(f"Skipping record {record.get('service_id')} due to missing coordinates")
                    continue

                # Add origin marker
                folium.Marker(
                    location=[
                        float(record['origin_latitude']), 
                        float(record['origin_longitude'])
                    ],
                    popup=folium.Popup(
                        _create_popup_content(record),
                        max_width=300
                    ),
                    icon=folium.Icon(
                        color=_get_marker_color(record.get('delay_minutes', 0)),
                        icon="info-sign"
                    )
                ).add_to(m)

                # Add destination marker
                folium.Marker(
                    location=[
                        float(record['destination_latitude']), 
                        float(record['destination_longitude'])
                    ],
                    popup=f"Destination: {record['destination']}",
                    icon=folium.Icon(color="blue", icon="flag")
                ).add_to(m)
            except Exception as e:
                logger.error(f"Error adding marker for record {record.get('service_id')}: {str(e)}")
                continue

        # Add Finsbury Park marker
        folium.Marker(
            location=[FPK_LATITUDE, FPK_LONGITUDE],
            popup="<b>Finsbury Park</b><br>Reference station for delays",
            icon=folium.Icon(color="purple", icon="info-sign")
        ).add_to(m)

        # Add legend
        _add_legend(m)

        # Get math path from MapConfig
        map_path = MapConfig.map_output_path()
        m.save(map_path)
        
        logger.info(f"✅ Map saved to: {map_path}")
        return map_path

    except Exception as e:
        logger.error(f"❌ Error generating map: {str(e)}")
        return None
