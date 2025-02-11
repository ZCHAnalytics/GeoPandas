# app/services/etl/merge/station_matcher.py

from typing import Dict, Set
from fuzzywuzzy import process

from app.core.logging_config import configure_logging

logger = configure_logging()

class StationMatcher:
    """Handles station name matching and corrections."""
    
    def __init__(self, station_names: Set[str]):
        self.station_names = station_names
        self.name_corrections = {
            "Letchworth": "Letchworth Garden City",
            "London Kings Cross": "King's Cross",
        }

    def find_best_matches(self, unmatched_stations: Set[str], 
                         confidence_threshold: int = 80) -> Dict[str, str]:
        """Find potential matches for unmatched station names."""
        suggestions = {}
        for station in unmatched_stations:
            match, score = process.extractOne(station, self.station_names)
            if score > confidence_threshold:
                suggestions[station] = match
        return suggestions

    def get_corrected_name(self, station_name: str) -> str:
        """Returns the corrected station name if it exists in corrections."""
        return self.name_corrections.get(station_name, station_name)