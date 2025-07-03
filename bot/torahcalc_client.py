"""
Client for interacting with TorahCalc API - "The Jewish Wolfram Alpha"
"""

import logging
import aiohttp
import asyncio
from datetime import datetime, date
from typing import Optional, Dict, List, Any, Union
import json

logger = logging.getLogger(__name__)

class TorahCalcClient:
    """Client for TorahCalc API - Advanced Jewish calculations and conversions"""
    
    def __init__(self):
        """Initialize the TorahCalc client"""
        self.session = None
        self.base_url = 'https://www.torahcalc.com/api'
        self.last_request_time = 0
        self.rate_limit_delay = 0.5  # 500ms between requests
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Union[Dict, List]]:
        """Make a request to the TorahCalc API"""
        await self._ensure_session()
        await self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            return None
    
    async def natural_language_query(self, query: str) -> Optional[Dict]:
        """Process natural language queries for calculations"""
        params = {'query': query}
        return await self._make_request('input', params)
    
    async def convert_biblical_units(self, unit_type: str, from_unit: str, to_unit: str, 
                                   amount: float = 1, opinion: str = None) -> Optional[Dict]:
        """Convert between biblical and modern units"""
        params = {
            'type': unit_type,
            'from': from_unit,
            'to': to_unit,
            'amount': amount
        }
        if opinion:
            params['opinion'] = opinion
        
        return await self._make_request('unitconverter', params)
    
    async def get_all_unit_conversions(self, unit_type: str, from_unit: str, 
                                     amount: float = 1, opinion: str = None) -> Optional[Dict]:
        """Get conversions to all compatible units"""
        params = {
            'type': unit_type,
            'from': from_unit,
            'amount': amount
        }
        if opinion:
            params['opinion'] = opinion
        
        return await self._make_request('unitcharts', params)
    
    async def get_gematria(self, text: str, method: str = 'standard') -> Optional[Dict]:
        """Calculate gematria values for Hebrew text"""
        # Note: This would use the natural language input for gematria calculations
        query = f"Gematria of {text}"
        return await self.natural_language_query(query)
    
    async def get_daily_learning(self, date_str: str = None) -> Optional[Dict]:
        """Get comprehensive daily learning schedule"""
        params = {}
        if date_str:
            params['date'] = date_str
        
        return await self._make_request('dailylearning', params)
    
    async def convert_date_greg_to_hebrew(self, year: int = None, month: int = None, 
                                        day: int = None, after_sunset: bool = False) -> Optional[Dict]:
        """Convert Gregorian date to Hebrew date"""
        params = {}
        if year is not None:
            params['year'] = year
        if month is not None:
            params['month'] = month
        if day is not None:
            params['day'] = day
        if after_sunset:
            params['afterSunset'] = after_sunset
        
        return await self._make_request('dateconverter/gregtoheb', params)
    
    async def convert_date_hebrew_to_greg(self, year: int, month: str, day: int) -> Optional[Dict]:
        """Convert Hebrew date to Gregorian date"""
        params = {
            'year': year,
            'month': month,
            'day': day
        }
        
        return await self._make_request('dateconverter/hebtogreg', params)
    
    async def get_birkas_hachama(self, year: int = None) -> Optional[Dict]:
        """Get next Birkas Hachama date"""
        params = {}
        if year:
            params['year'] = year
        
        return await self._make_request('hachama', params)
    
    async def get_zmanim(self, location: str = "New York", date_str: str = None) -> Optional[Dict]:
        """Get halachic times (zmanim) for location and date"""
        # This would use natural language query for zmanim
        query = f"Zmanim for {location}"
        if date_str:
            query += f" on {date_str}"
        
        return await self.natural_language_query(query)
    
    async def calculate_measurement(self, measurement_query: str) -> Optional[Dict]:
        """Calculate biblical measurements using natural language"""
        return await self.natural_language_query(measurement_query)
    
    async def get_coin_values(self, coin_type: str, amount: float = 1) -> Optional[Dict]:
        """Get biblical coin values in modern currency"""
        return await self.get_all_unit_conversions('coins', coin_type, amount)
    
    async def get_volume_conversions(self, volume_unit: str, amount: float = 1, 
                                   opinion: str = 'rabbi_avraham_chaim_naeh') -> Optional[Dict]:
        """Get volume conversions with halachic opinions"""
        return await self.get_all_unit_conversions('volume', volume_unit, amount, opinion)
    
    async def get_length_conversions(self, length_unit: str, amount: float = 1, 
                                   opinion: str = 'rabbi_avraham_chaim_naeh') -> Optional[Dict]:
        """Get length conversions with halachic opinions"""
        return await self.get_all_unit_conversions('length', length_unit, amount, opinion)
    
    async def get_time_conversions(self, time_unit: str, amount: float = 1) -> Optional[Dict]:
        """Get Jewish time unit conversions"""
        return await self.get_all_unit_conversions('time', time_unit, amount)
    
    async def search_calculations(self, query_type: str, search_term: str) -> List[Dict]:
        """Search for specific types of calculations"""
        results = []
        
        try:
            if query_type.lower() in ['gematria', 'numerology']:
                result = await self.get_gematria(search_term)
                if result:
                    results.append({
                        'type': 'Gematria Calculation',
                        'query': search_term,
                        'result': result
                    })
            
            elif query_type.lower() in ['units', 'measurement', 'convert']:
                result = await self.calculate_measurement(f"Convert {search_term}")
                if result:
                    results.append({
                        'type': 'Unit Conversion',
                        'query': search_term,
                        'result': result
                    })
            
            elif query_type.lower() in ['learning', 'study', 'daf']:
                result = await self.get_daily_learning()
                if result:
                    results.append({
                        'type': 'Daily Learning',
                        'query': search_term,
                        'result': result
                    })
            
            elif query_type.lower() in ['date', 'calendar', 'hebrew']:
                if 'hebrew' in search_term.lower() or 'jewish' in search_term.lower():
                    result = await self.convert_date_greg_to_hebrew()
                    if result:
                        results.append({
                            'type': 'Date Conversion',
                            'query': search_term,
                            'result': result
                        })
            
            # Try natural language processing for any query
            natural_result = await self.natural_language_query(search_term)
            if natural_result:
                results.append({
                    'type': 'Natural Language Calculation',
                    'query': search_term,
                    'result': natural_result
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching calculations: {e}")
            return []
    
    async def get_comprehensive_study_data(self, date_str: str = None) -> Optional[Dict]:
        """Get comprehensive study data including learning and conversions"""
        try:
            # Get daily learning
            daily_learning = await self.get_daily_learning(date_str)
            
            # Get current Hebrew date
            hebrew_date = await self.convert_date_greg_to_hebrew()
            
            # Get some common unit examples
            amah_conversions = await self.get_length_conversions('amah')
            kezayis_conversions = await self.get_volume_conversions('kezayis')
            
            return {
                'daily_learning': daily_learning,
                'hebrew_date': hebrew_date,
                'common_measurements': {
                    'amah_length': amah_conversions,
                    'kezayis_volume': kezayis_conversions
                },
                'capabilities': [
                    'Biblical unit conversions',
                    'Gematria calculations',
                    'Daily learning schedules',
                    'Hebrew calendar conversions',
                    'Halachic time calculations',
                    'Natural language processing'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive study data: {e}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()