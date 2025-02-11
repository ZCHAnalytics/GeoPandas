# app/services/etl/map.py
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import folium
from folium import Element
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
# Project Modules
from app.core.logging_config import configure_logging

logger = configure_logging()

TABLE_NAME = "arrivals_tracking"

class TrainDelayMap:
    """Handles the generation of train delay maps using Folium."""
    
    def __init__(self):
        # Define constants
        self.FPK_LATITUDE = 51.5643002449157
        self.FPK_LONGITUDE = -0.106284978884699
        
        # Ensure the maps directory exists
        self.output_dir = os.path.join('data', 'maps')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define the default map output path
        self.map_output_path = os.path.join(
            self.output_dir,
            f"train_delays_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )

    async def fetch_delay_data(self, db: AsyncSession, hours: int = 1) -> List[Dict[str, Any]]:
        """
        Fetches recent train delay data from PostGIS.
        
        Args:
            db: Database session
            hours: Number of hours of historical data to fetch
            
        Returns:
            List of dictionaries containing train delay data
        """
        try:
            query = text(f"""
                SELECT 
                    run_date,
                    service_id,
                    operator,
                    origin,
                    origin_crs,
                    ST_X(origin_geom::geometry) as origin_longitude,
                    ST_Y(origin_geom::geometry) as origin_latitude,
                    destination,
                    destination_crs,
                    ST_X(destination_geom::geometry) as destination_longitude,
                    ST_Y(destination_geom::geometry) as destination_latitude,
                    scheduled_arrival,
                    actual_arrival,
                    delay_minutes,
                    is_passenger_train
                FROM {TABLE_NAME}
                WHERE is_passenger_train = TRUE
                ORDER BY delay_minutes DESC  -- Order by delay_minutes in descending order
                LIMIT 100  -- Fetch only the top 100 records
                """)
            
            result = await db.execute(query)
            delay_data = [row._asdict() for row in result.fetchall()] # Convert to dict
            
            logger.info("✅ Retrieved %d records from database", len(delay_data))
            return delay_data
            
        except Exception as e:
            logger.error("❌ Error fetching delay data: %s", str(e))
            raise

    def _get_marker_color(self, delay: int) -> str:
        """Determines marker color based on delay severity."""
        if delay < 0:
            return "green"  # Early
        elif delay > 10:
            return "red"    # Significant delay
        else:
            return "orange" # Minor delay or on time

    def _create_popup_content(self, row: Dict[str, Any], default_station="Finsbury Park") -> str:
        """Creates HTML content for marker popups."""
        popup_info = (
            f"<b>Origin:</b> {row['origin']} (CRS: {row['origin_crs']})<br>"
            f"<b>Destination:</b> {row['destination']} (CRS: {row['destination_crs']})<br>"
            f"<b>Operator:</b> {row['operator']}<br>"
            f"<b>Scheduled Arrival at {default_station}:</b> {row['scheduled_arrival'].strftime('%H:%M')}<br>"  # Include default station
            f"<b>Actual Arrival at {default_station}:</b> {row['actual_arrival'].strftime('%H:%M')}<br>"  # Include default station
        )
        
        delay = row['delay_minutes']
        if delay is not None:
            if delay < 0:
                popup_info += f"<b>Early:</b> {abs(delay)} min"
            else:
                popup_info += f"<b>Delay:</b> {delay} min"
                
        return popup_info

    def _add_legend(self, map_obj: folium.Map) -> None:
        """Adds a legend to the map."""
        legend_html = """
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 250px; height: 130px; 
                        border:2px solid grey; z-index:9999; font-size:14px; 
                        background-color:white; padding: 10px;">
                <b>Legend:</b><br>
                <i class="fa fa-circle" style="color:green"></i> Early<br>
                <i class="fa fa-circle" style="color:orange"></i> On Time/Minor Delay<br>
                <i class="fa fa-circle" style="color:red"></i> Significant Delay<br>
                <i class="fa fa-flag" style="color:blue"></i> Destination<br>
                <br><b>Note:</b> Delays refer to arrivals at Finsbury Park.
            </div>
        """
        map_obj.get_root().html.add_child(Element(legend_html))

    async def generate_map(self, db: AsyncSession, hours: int = 1) -> Optional[str]:
        """
        Generates an HTML map showing train delays.
        
        Args:
            db: Database session
            hours: Number of hours of historical data to display
            
        Returns:
            Path to the generated HTML map file
        """
        try:
            # Fetch data from PostGIS
            delay_data = await self.fetch_delay_data(db, hours)
            
            if not delay_data:
                logger.warning("⚠️ No delay data available for map generation")
                return None
            
            # Create base map
            m = folium.Map(
                location=[self.FPK_LATITUDE, self.FPK_LONGITUDE],
                zoom_start=10,
                tiles="CartoDB positron"
            )
            
            # Add markers for each train service
            for row in delay_data:
                # Create origin marker
                if row['origin_latitude'] is not None and row['origin_longitude'] is not None:
                    
                    folium.Marker(
                        location=[row['origin_latitude'], row['origin_longitude']],
                        popup=folium.Popup(
                            self._create_popup_content(row),
                            max_width=300
                        ),
                        icon=folium.Icon(
                            color=self._get_marker_color(row['delay_minutes']),
                            icon="info-sign"
                        )
                    ).add_to(m)
                
                if row['destination_latitude'] is not None and row['destination_longitude'] is not None:
                    
                    # Create destination marker with default station in popup 
                    
                    folium.Marker(
                    location=[row['destination_latitude'], row['destination_longitude']],
                    popup=folium.Popup(self._create_popup_content(row, default_station="Finsbury Park"), max_width=300),  # Use _create_popup_content
                    icon=folium.Icon(color="blue", icon="flag"),
                    tooltip=f"Destination: {row['destination']}"
                ).add_to(m)
            
            # Add Finsbury Park marker
            folium.Marker(
                location=[self.FPK_LATITUDE, self.FPK_LONGITUDE],
                popup="<b>Finsbury Park</b><br>Reference station for delays",
                icon=folium.Icon(color="purple", icon="info-sign")
            ).add_to(m)
            
            # Add legend
            self._add_legend(m)
            
            # Save map
            m.save(self.map_output_path)
            logger.info("✅ Map generated successfully at: %s", 
                       self.map_output_path)
            
            return self.map_output_path
            
        except Exception as e:
            logger.error("❌ Error generating map: %s", str(e))
            return None 
