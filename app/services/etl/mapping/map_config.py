# app/services/etl/map/map_config.py

from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class MapConfig:
    """Map configuration and constants."""
    
    # Finsbury Park coordinates
    FPK_LATITUDE: float = 51.5643002449157
    FPK_LONGITUDE: float = -0.106284978884699
    
    # Class Attribute
    OUTPUT_DIR: str = os.path.join('data', 'maps')
    
    @staticmethod
    def map_output_path() -> str:
        """Generate timestamped output path for map."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(
            MapConfig.OUTPUT_DIR,
            f"train_delays_map_{timestamp}.html"
        )
    
# ENsure directories exist at import
os.makedirs(MapConfig.OUTPUT_DIR, exist_ok=True)