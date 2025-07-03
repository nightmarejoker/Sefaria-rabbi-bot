"""
Client for interacting with the Sefaria API
"""
import aiohttp
import asyncio
import logging
import random
from typing import Optional, Dict, List, Any
from urllib.parse import quote

logger = logging.getLogger(__name__)

class SefariaClient:
    """Client for Sefaria API interactions"""
    
    def __init__(self):
        self.base_url = "https://www.sefaria.org/api"
        self.session = None
        self._rate_limit_delay = 1.0  # Seconds between requests
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
        """Implement basic rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the Sefaria API"""
        await self._ensure_session()
        await self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.warning(f"Resource not found: {url}")
                    return None
                else:
                    logger.error(f"API request failed with status {response.status}: {url}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error during API request: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            return None
    
    async def get_random_text(self, category: Optional[str] = None) -> Optional[Dict]:
        """Get a random text from Sefaria"""
        try:
            # First, get a list of texts
            if category:
                # Get texts from specific category
                texts_data = await self._make_request(f"index")
                if not texts_data:
                    return None
                
                # Filter texts by category (simplified approach)
                available_texts = []
                for text in texts_data:
                    if isinstance(text, dict) and 'title' in text:
                        if category.lower() in text.get('categories', []).lower() if text.get('categories') else False:
                            available_texts.append(text['title'])
                
                if not available_texts:
                    # Fallback to all texts if category not found
                    available_texts = [text['title'] for text in texts_data if isinstance(text, dict) and 'title' in text]
            else:
                # Get all available texts
                texts_data = await self._make_request("index")
                if not texts_data:
                    return None
                
                available_texts = [text['title'] for text in texts_data if isinstance(text, dict) and 'title' in text]
            
            if not available_texts:
                return None
            
            # Pick a random text
            random_title = random.choice(available_texts)
            
            # Get the text content
            return await self.get_text(random_title)
            
        except Exception as e:
            logger.error(f"Error getting random text: {e}")
            return None
    
    async def get_text(self, reference: str) -> Optional[Dict]:
        """Get a specific text by reference"""
        try:
            # Clean and encode the reference
            reference = reference.strip()
            encoded_ref = quote(reference, safe='')
            
            # Get the text
            text_data = await self._make_request(f"texts/{encoded_ref}")
            
            if not text_data:
                return None
            
            # Ensure we have the required fields
            if 'text' not in text_data and 'he' not in text_data:
                logger.warning(f"No text content found for reference: {reference}")
                return None
            
            # For single verse requests (e.g. "Genesis 1:1"), show only that verse
            if ':' in reference and not '-' in reference:
                # This is a single verse request, show only one verse
                if 'text' in text_data and isinstance(text_data['text'], list):
                    if len(text_data['text']) > 1:
                        text_data['text'] = text_data['text'][:1]  # Just first verse
                        text_data['single_verse'] = True
                
                if 'he' in text_data and isinstance(text_data['he'], list):
                    if len(text_data['he']) > 1:
                        text_data['he'] = text_data['he'][:1]  # Just first verse
                        text_data['single_verse'] = True
            else:
                # For ranges or chapters, limit to first 3 verses to avoid overwhelming messages
                if 'text' in text_data and isinstance(text_data['text'], list):
                    if len(text_data['text']) > 3:
                        text_data['text'] = text_data['text'][:3]
                        text_data['truncated'] = True
                
                if 'he' in text_data and isinstance(text_data['he'], list):
                    if len(text_data['he']) > 3:
                        text_data['he'] = text_data['he'][:3]
                        text_data['truncated'] = True
            
            return text_data
            
        except Exception as e:
            logger.error(f"Error getting text for reference '{reference}': {e}")
            return None
    
    async def search_texts(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for texts matching the query"""
        try:
            params = {
                'q': query,
                'limit': limit
            }
            
            search_data = await self._make_request("search-wrapper", params)
            
            if not search_data or 'text_hits' not in search_data:
                return []
            
            results = []
            for hit in search_data['text_hits'][:limit]:
                if isinstance(hit, dict):
                    results.append({
                        'ref': hit.get('ref', ''),
                        'text': hit.get('text', ''),
                        'title': hit.get('title', '')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching texts for query '{query}': {e}")
            return []
    
    async def get_daily_text(self) -> Optional[Dict]:
        """Get today's daily text (Torah portion, etc.)"""
        try:
            # Try different approaches to get daily content
            daily_options = [
                "Psalms 1:1",  # Daily psalm
                "Pirkei Avot 1:1",  # Ethics of the Fathers
                "Talmud Berakhot 2a",  # Daily Talmud page
                "Genesis 1:1",  # Torah beginning
                "Deuteronomy 6:4"  # Shema
            ]
            
            # Pick a daily text based on today's date (simple rotation)
            import datetime
            today = datetime.date.today()
            daily_index = today.toordinal() % len(daily_options)
            chosen_ref = daily_options[daily_index]
            
            logger.info(f"Getting daily text: {chosen_ref}")
            return await self.get_text(chosen_ref)
            
        except Exception as e:
            logger.error(f"Error getting daily text: {e}")
            return None
    
    async def get_categories(self) -> List[str]:
        """Get list of available text categories"""
        try:
            index_data = await self._make_request("index")
            
            if not index_data:
                return []
            
            categories = set()
            for text in index_data:
                if isinstance(text, dict) and 'categories' in text:
                    text_categories = text['categories']
                    if isinstance(text_categories, list):
                        categories.update(text_categories)
            
            return sorted(list(categories))
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
