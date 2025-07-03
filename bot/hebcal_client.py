"""
Client for interacting with the Hebcal API for Jewish calendar data
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime, date

logger = logging.getLogger(__name__)

class HebcalClient:
    """Client for Hebcal API interactions"""
    
    def __init__(self):
        self.base_url = "https://www.hebcal.com"
        self.session = None
        self._rate_limit_delay = 0.2  # 90 requests per 10 seconds = ~0.11s delay
        self._last_request_time = 0
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Discord-Sefaria-Bot/1.0'
                }
            )
    
    async def _rate_limit(self):
        """Implement rate limiting for Hebcal API"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the Hebcal API"""
        await self._ensure_session()
        await self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Rate limited by Hebcal API, waiting longer...")
                    await asyncio.sleep(2)
                    return None
                else:
                    logger.error(f"Hebcal API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making request to Hebcal: {e}")
            return None
    
    async def get_shabbat_times(self, location: str = "New York") -> Optional[Dict]:
        """Get Shabbat candle lighting and havdalah times"""
        try:
            # For simplicity, use geoid for major cities
            location_map = {
                "new york": "5128581",
                "los angeles": "5368361", 
                "chicago": "4887398",
                "miami": "4164138",
                "jerusalem": "281184",
                "tel aviv": "293397",
                "london": "2643743",
                "paris": "2988507"
            }
            
            geonameid = location_map.get(location.lower(), "5128581")  # Default to NYC
            
            params = {
                "cfg": "json",
                "geonameid": geonameid,
                "M": "on"  # Include havdalah times
            }
            
            data = await self._make_request("shabbat", params)
            return data
            
        except Exception as e:
            logger.error(f"Error getting Shabbat times: {e}")
            return None
    
    async def get_jewish_holidays(self, year: Optional[int] = None) -> Optional[List[Dict]]:
        """Get Jewish holidays for a specific year"""
        try:
            if year is None:
                year = datetime.now().year
            
            params = {
                "v": "1",
                "cfg": "json",
                "year": year,
                "maj": "on",  # Major holidays only
                "min": "on",  # Minor holidays
                "mod": "on",  # Modern holidays
                "nx": "on",   # Rosh Chodesh
                "ss": "on",   # Special Shabbatot
                "mf": "on"    # Minor fasts
            }
            
            data = await self._make_request("hebcal", params)
            
            if data and "items" in data:
                return data["items"]
            return None
            
        except Exception as e:
            logger.error(f"Error getting Jewish holidays: {e}")
            return None
    
    async def get_torah_reading(self, date_obj: Optional[date] = None) -> Optional[Dict]:
        """Get Torah reading for a specific date"""
        try:
            if date_obj is None:
                date_obj = date.today()
            
            params = {
                "v": "1", 
                "cfg": "json",
                "start": date_obj.strftime("%Y-%m-%d"),
                "end": date_obj.strftime("%Y-%m-%d"),
                "s": "on"  # Include Torah readings
            }
            
            data = await self._make_request("hebcal", params)
            
            if data and "items" in data:
                for item in data["items"]:
                    if "torah" in item.get("category", "").lower() or "parashat" in item.get("title", "").lower():
                        return item
            return None
            
        except Exception as e:
            logger.error(f"Error getting Torah reading: {e}")
            return None
    
    async def convert_hebrew_date(self, gregorian_date: date) -> Optional[Dict]:
        """Convert Gregorian date to Hebrew date"""
        try:
            params = {
                "cfg": "json",
                "gy": gregorian_date.year,
                "gm": gregorian_date.month,
                "gd": gregorian_date.day,
                "g2h": "1"
            }
            
            data = await self._make_request("converter", params)
            return data
            
        except Exception as e:
            logger.error(f"Error converting Hebrew date: {e}")
            return None
    
    async def get_zmanim(self, location: str = "New York", date_obj: Optional[date] = None) -> Optional[Dict]:
        """Get halachic times (zmanim) for a location and date"""
        try:
            if date_obj is None:
                date_obj = date.today()
            
            # Use same location mapping as Shabbat times
            location_map = {
                "new york": "5128581",
                "los angeles": "5368361", 
                "chicago": "4887398",
                "miami": "4164138",
                "jerusalem": "281184",
                "tel aviv": "293397",
                "london": "2643743",
                "paris": "2988507"
            }
            
            geonameid = location_map.get(location.lower(), "5128581")
            
            params = {
                "cfg": "json",
                "geonameid": geonameid,
                "date": date_obj.strftime("%Y-%m-%d")
            }
            
            data = await self._make_request("zmanim", params)
            return data
            
        except Exception as e:
            logger.error(f"Error getting zmanim: {e}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()