"""
Client for interacting with Chabad.org content and services
"""
import aiohttp
import asyncio
import logging
import hashlib
import hmac
import base64
import time
from typing import Dict, List, Optional, Union
from urllib.parse import quote, urljoin
import json
import re

logger = logging.getLogger(__name__)

class ChabadClient:
    """Client for Chabad.org content and services"""
    
    def __init__(self, public_key: Optional[str] = None, secret_key: Optional[str] = None):
        """Initialize the Chabad client"""
        self.base_url = "https://www.chabad.org"
        self.api_url = "https://api.chabad.org"
        self.mychabad_url = "https://www.mychabad.org"
        
        # API keys (if available)
        self.public_key = public_key
        self.secret_key = secret_key
        
        self.session = None
        self.last_request_time = 0
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_request_time < 1.0:
            await asyncio.sleep(1.0 - (current_time - self.last_request_time))
        self.last_request_time = asyncio.get_event_loop().time()
    
    def _create_auth_header(self, route: str, user: str = "") -> Optional[str]:
        """Create authentication header for Chabad.org API if credentials available"""
        if not self.public_key or not self.secret_key:
            return None
            
        timestamp = int(time.time())
        
        # Create signature string
        to_sign = "|".join(filter(None, [self.public_key, user, str(timestamp), route]))
        
        # Decode secret and create HMAC
        secret_bytes = base64.b64decode(self.secret_key.encode())
        signature = hmac.new(secret_bytes, to_sign.encode(), hashlib.sha1)
        signature_b64 = base64.urlsafe_b64encode(signature.digest()).decode().rstrip('=')
        
        # Create header
        header_parts = "|".join(filter(None, [self.public_key, user, str(timestamp)]))
        return f"h={header_parts}; s={signature_b64}"
    
    async def _make_request(self, url: str, params: Optional[Dict] = None, use_auth: bool = False) -> Optional[Dict]:
        """Make a request to Chabad.org"""
        await self._ensure_session()
        await self._rate_limit()
        
        headers = {}
        if use_auth:
            auth_header = self._create_auth_header(url)
            if auth_header:
                headers['Authorization'] = auth_header
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        # Parse HTML content for structured data
                        text = await response.text()
                        return self._parse_html_content(text)
                else:
                    logger.error(f"Chabad request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making Chabad request: {e}")
            return None
    
    def _parse_html_content(self, html: str) -> Dict:
        """Parse HTML content to extract structured information"""
        # Extract JSON-LD structured data
        import re
        
        # Look for JSON-LD data
        jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        jsonld_matches = re.findall(jsonld_pattern, html, re.DOTALL | re.IGNORECASE)
        
        result = {}
        
        for match in jsonld_matches:
            try:
                data = json.loads(match.strip())
                result['structured_data'] = data
                break
            except json.JSONDecodeError:
                continue
        
        # Extract title
        title_pattern = r'<title[^>]*>(.*?)</title>'
        title_match = re.search(title_pattern, html, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1).strip()
        
        # Extract meta description
        desc_pattern = r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
        desc_match = re.search(desc_pattern, html, re.IGNORECASE)
        if desc_match:
            result['description'] = desc_match.group(1).strip()
        
        return result
    
    async def get_daily_study(self) -> Optional[Dict]:
        """Get daily study content from Chabad.org"""
        url = f"{self.base_url}/library/article_cdo/aid/3146/jewish/Daily-Study.htm"
        return await self._make_request(url)
    
    async def get_daily_wisdom(self) -> Optional[Dict]:
        """Get daily wisdom/quote from Chabad.org"""
        url = f"{self.base_url}/library/article_cdo/aid/3147/jewish/Daily-Wisdom.htm"
        return await self._make_request(url)
    
    async def get_daily_mitzvah(self) -> Optional[Dict]:
        """Get daily mitzvah from Chabad.org"""
        url = f"{self.base_url}/library/article_cdo/aid/3148/jewish/Daily-Mitzvah.htm"
        return await self._make_request(url)
    
    async def search_articles(self, query: str, limit: int = 10) -> List[Dict]:
        """Search articles on Chabad.org"""
        url = f"{self.base_url}/search"
        params = {
            'q': query,
            'limit': limit
        }
        
        result = await self._make_request(url, params)
        if result:
            return [result]  # Wrapped in list for consistency
        return []
    
    async def get_chassidic_calendar(self) -> Optional[Dict]:
        """Get Chassidic calendar information"""
        url = f"{self.base_url}/calendar"
        return await self._make_request(url)
    
    async def get_daily_tanya(self) -> Optional[Dict]:
        """Get today's Tanya lesson"""
        url = f"{self.base_url}/library/tanya"
        return await self._make_request(url)
    
    async def get_weekly_torah_study(self) -> Optional[Dict]:
        """Get weekly Torah study materials"""
        url = f"{self.base_url}/parshah"
        return await self._make_request(url)
    
    async def get_chassidic_stories(self, limit: int = 5) -> List[Dict]:
        """Get Chassidic stories"""
        url = f"{self.base_url}/library/article_cdo/aid/3149/jewish/Stories.htm"
        result = await self._make_request(url)
        if result:
            return [result]
        return []
    
    async def get_chabad_directory(self, location: str = "") -> Optional[Dict]:
        """Search Chabad centers directory"""
        url = f"{self.base_url}/centers"
        params = {}
        if location:
            params['location'] = location
            
        return await self._make_request(url, params)
    
    async def get_jewish_learning_path(self, topic: str = "") -> Optional[Dict]:
        """Get Jewish learning resources by topic"""
        url = f"{self.base_url}/library"
        params = {}
        if topic:
            params['topic'] = topic
            
        return await self._make_request(url, params)
    
    async def get_multimedia_content(self, content_type: str = "video") -> List[Dict]:
        """Get multimedia content (videos, audio)"""
        url = f"{self.base_url}/multimedia/{content_type}"
        result = await self._make_request(url)
        if result:
            return [result]
        return []
    
    async def get_rabbi_responses(self, category: str = "") -> List[Dict]:
        """Get Ask the Rabbi responses"""
        url = f"{self.base_url}/asktherabbi"
        params = {}
        if category:
            params['category'] = category
            
        result = await self._make_request(url, params)
        if result:
            return [result]
        return []
    
    async def get_kosher_info(self, query: str = "") -> Optional[Dict]:
        """Get kosher certification and food information"""
        url = f"{self.base_url}/kosher"
        params = {}
        if query:
            params['q'] = query
            
        return await self._make_request(url, params)
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()