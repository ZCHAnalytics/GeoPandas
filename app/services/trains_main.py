# app/services/trains_main.py
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
from aiohttp import ClientSession, BasicAuth
from app.core.config import settings
from app.core.logging_config import configure_logging
print("") 

logger = configure_logging()

class RTTClient:
    """Client for Real Time Trains API."""

    def __init__(self):
        self.base_url = settings.base_url 
        self.auth = BasicAuth(settings.RTT_USERNAME, settings.RTT_PASSWORD)
        self.timeout=30

    async def _fetch_data(self, url: str) -> Dict[str, Any]:
        # Fetch data asynchronously using aiohttp.
        try:
            async with ClientSession() as session:
                async with session.get(url=url, auth=self.auth, timeout=self.timeout) as response:
                    response.raise_for_status()  # Raise an exception for bad responses
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error("❌ API Request Failed: %s", str(e))
            return {"error": f"Failed to fetch train data: {str(e)}"}
        except Exception as e: 
            logger.error("❌ Error fetching data: %s", str(e))
            return {"error": str(e)}


    def _build_url(self, station: str, date: str, to_station: Optional[str] = None) -> str:
        """
        Build the API request URL.
        
        Args:
            station: Station code
            date: Formatted date string
            to_station: Optional destination stations for filtered queries

        Returns:
            Complete API URL
        """
        try:
            # Split the date into year, mpnth and day components
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day

            # Ensure month and day are two digits to match RTT format 
            month_str = f"{month:02d}"
            day_str = f"{day:02d}"
            
            # Build the base URL
            url = f"{self.base_url}/{station}/{year}/{month_str}/{day_str}"
            # if destination station specified, add 
            if to_station:
                url += f"/to/{to_station}"
            #append '/arrivals' 
            url += "/arrivals"
            return url
        
        except ValueError as e:
            logger.error("❌ Invalid date format: %s", date)
            return None 

    def _parse_service(self, service: Dict[str, Any], station: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single service from the API response.
        
        Args:
            service: Raw service data from API
            station: Station code to filter for
            
        Returns:
            Parsed service data or None if invalid
        """
        loc = service.get("locationDetail", {})
        
        # Only include arrivals at the searched station
        if loc.get("crs") != station:
            return None
        
        return {
            "run_date": service.get("runDate"),
            "service_id": service.get("serviceUid"),
            "operator": service.get("atocName"),
            "is_passenger_train": service.get("isPassenger", False),
            # Scheduled & actual arrival times
            "scheduled_arrival": loc.get("gbttBookedArrival"),
            "actual_arrival": loc.get("realtimeArrival"),
            "is_actual": loc.get("realtimeArrivalActual", False),
            # Origin & destination
            "origin": (loc.get("origin", [{}])[0].get("description", "UNKNOWN") 
                      if loc.get("origin") else "UNKNOWN"),
            "destination": (loc.get("destination", [{}])[0].get("description", "UNKNOWN") 
                          if loc.get("destination") else "UNKNOWN"),
            # Additional info
            "was_scheduled_to_stop": loc.get("isCall", False),
            "stop_status": loc.get("displayAs", "UNKNOWN")
        }

    async def get_train_arrivals(self, station: str, date: str) -> Dict[str, Any]:
        """
        Fetch train arrivals at a given station on a given date.
        
        Args:
            station: Station code (e.g., "FPK")
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing train arrivals or error message
        """
        
        url = self._build_url(station, date)         
        try:
            async with ClientSession() as session:
                async with session.get(url, auth=self.auth, timeout=self.timeout) as response:
                    response.raise_for_status()
                    response_json = await response.json()

                    # Validate response structure
                    services = response_json.get("services", [])
                    if not isinstance(services, list):
                        logger.error("❌ Invalid 'services' format in API response")
                        return {"error": "Invalid response format from RTT API"}
                    
                    # Parse services
                    arrivals = []
                    for service in services:
                        parsed_service = self._parse_service(service, station)
                        if parsed_service:
                            arrivals.append(parsed_service)
                    
                    if arrivals:
                        logger.info("✅ Retrieved %d arrivals for %s on %s", 
                                len(arrivals), station, date)
                        return {"services": arrivals}
                    else:
                        logger.warning("⚠️ No valid arrivals found for %s on %s", 
                                    station, date)
                        return {"error": "No valid arrivals found"}
                    
        except aiohttp.ClientError as e:
            logger.error("❌ API Request Failed: %s", str(e))
            return {"error": f"Failed to fetch train data: {str(e)}"}
        
        except Exception as e:
            logger.error("❌ Error fetching data: %s", str(e))
            return {"error": "st(e)"}
        
        

# Create global RTT client instance
rtt_client = RTTClient()

# Export the async function for backward compatibility
async def get_train_arrivals(station: str, date: str) -> Dict[str, Any]:
    return await rtt_client.get_train_arrivals(station, date)


"""
if __name__ == "__main__":
    
    # Test the RTT client directly.
    
    import sys
    from datetime import datetime, timedelta
    
    # Test with Finsbury Park for yesterday
    station = "FPK"
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"\nTesting RTT client with:")
    print(f"Station: {station}")
    print(f"Date: {test_date}")
    
    result = get_train_arrivals(station, test_date)
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
    
    services = result.get("services", [])
    print(f"\n✅ Retrieved {len(services)} services")
    
    if services:
        print("\nSample service:")
        sample = services[0]
        for key, value in sample.items():
            print(f"{key}: {value}")

"""