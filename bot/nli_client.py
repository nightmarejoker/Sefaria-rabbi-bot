"""
Client for interacting with the National Library of Israel API
"""
import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Union
from urllib.parse import quote

logger = logging.getLogger(__name__)

class NLIClient:
    """Client for National Library of Israel API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the NLI client"""
        import os
        self.base_url = "https://api.nli.org.il/openlibrary"
        # Load API key from environment or use provided key
        self.api_key = api_key or os.getenv('NLI_API_KEY', 'DVQyidFLOAjp12ib92pNJPmflmB5IessOq1CJQDK')
        self.session = None
        self.last_request_time = 0
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _rate_limit(self):
        """Implement rate limiting for NLI API"""
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_request_time < 1.0:
            await asyncio.sleep(1.0 - (current_time - self.last_request_time))
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the NLI API"""
        await self._ensure_session()
        await self._rate_limit()
        
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"NLI API request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making NLI API request: {e}")
            return None
    
    async def search_hebrew_manuscripts(self, query: str, limit: int = 10) -> Optional[List[Dict]]:
        """Search for Hebrew manuscripts"""
        params = {
            'query': f'title,contains,{quote(query)},AND;material_type,exact,manuscript',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_historical_photos(self, query: str, limit: int = 10) -> Optional[List[Dict]]:
        """Search for historical photographs"""
        params = {
            'query': f'title,contains,{quote(query)},AND;material_type,exact,photograph',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_jewish_books(self, query: str, language: str = 'heb', limit: int = 10) -> Optional[List[Dict]]:
        """Search for Jewish books in Hebrew or other languages"""
        params = {
            'query': f'title,contains,{quote(query)},AND;language,exact,{language}',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_maps(self, location: str, limit: int = 10) -> Optional[List[Dict]]:
        """Search for historical maps"""
        params = {
            'query': f'title,contains,{quote(location)},AND;material_type,exact,map',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_audio_recordings(self, query: str, limit: int = 10) -> Optional[List[Dict]]:
        """Search for audio recordings"""
        params = {
            'query': f'title,contains,{quote(query)},AND;material_type,exact,audio',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_by_creator(self, creator: str, limit: int = 10) -> Optional[List[Dict]]:
        """Search for works by a specific creator/author"""
        params = {
            'query': f'creator,contains,{quote(creator)}',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_by_subject(self, subject: str, limit: int = 10) -> Optional[List[Dict]]:
        """Search for works by subject"""
        params = {
            'query': f'subject,contains,{quote(subject)}',
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_by_date_range(self, start_year: int, end_year: int, query: str = "", limit: int = 10) -> Optional[List[Dict]]:
        """Search for works within a date range"""
        if query:
            search_query = f'title,contains,{quote(query)},AND;start_date,range,{start_year},{end_year}'
        else:
            search_query = f'start_date,range,{start_year},{end_year}'
            
        params = {
            'query': search_query,
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def search_jerusalem_collection(self, query: str = "", limit: int = 10) -> Optional[List[Dict]]:
        """Search specifically for Jerusalem-related items"""
        if query:
            search_query = f'title,contains,{quote(query)},AND;subject,contains,Jerusalem'
        else:
            search_query = 'subject,contains,Jerusalem'
            
        params = {
            'query': search_query,
            'items_per_page': str(limit),
            'output_format': 'json'
        }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            return result['result'].get('records', [])
        return []
    
    async def get_random_item(self, material_type: str = "") -> Optional[Dict]:
        """Get a random item from the collection"""
        # Use a broad search and pick randomly
        import random
        
        if material_type:
            params = {
                'query': f'material_type,exact,{material_type}',
                'items_per_page': '50',
                'output_format': 'json'
            }
        else:
            params = {
                'query': 'language,exact,heb',  # Broad search
                'items_per_page': '50',
                'output_format': 'json'
            }
        
        result = await self._make_request('search', params)
        if result and 'result' in result:
            records = result['result'].get('records', [])
            if records:
                return random.choice(records)
        return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()