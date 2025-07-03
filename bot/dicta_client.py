"""
Client for interacting with Dicta Israel Center for Text Analysis
"""
import aiohttp
import asyncio
import logging
import json
from typing import Dict, List, Optional, Union
from urllib.parse import quote
import random

logger = logging.getLogger(__name__)

class DictaClient:
    """Client for Dicta Israel Center for Text Analysis"""
    
    def __init__(self):
        """Initialize the Dicta client"""
        self.base_url = "https://library.dicta.org.il"
        self.files_url = "https://files.dicta.org.il"
        self.books_json_url = "https://raw.githubusercontent.com/Dicta-Israel-Center-for-Text-Analysis/Dicta-Library-Download/main/books.json"
        
        self.session = None
        self.last_request_time = 0
        self.books_cache = None
        
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
    
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Union[Dict, List]]:
        """Make a request to Dicta resources"""
        await self._ensure_session()
        await self._rate_limit()
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        text = await response.text()
                        # Try to parse as JSON if it looks like JSON
                        if text.strip().startswith('[') or text.strip().startswith('{'):
                            try:
                                return json.loads(text)
                            except json.JSONDecodeError:
                                pass
                        return {'content': text}
                else:
                    logger.error(f"Dicta request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making Dicta request: {e}")
            return None
    
    async def get_books_library(self) -> List[Dict]:
        """Get the complete Dicta books library catalog"""
        if self.books_cache is None:
            result = await self._make_request(self.books_json_url)
            if result and isinstance(result, list):
                self.books_cache = result
            else:
                self.books_cache = []
        return self.books_cache
    
    async def search_books(self, query: str, category: str = "", author: str = "", limit: int = 10) -> List[Dict]:
        """Search books in the Dicta library"""
        books = await self.get_books_library()
        
        # Filter books based on search criteria
        filtered_books = []
        query_lower = query.lower()
        category_lower = category.lower()
        author_lower = author.lower()
        
        for book in books:
            match = False
            
            # Search in display name (both Hebrew and English)
            if (query_lower in book.get('displayName', '').lower() or 
                query_lower in book.get('displayNameEnglish', '').lower()):
                match = True
            
            # Search in author (both Hebrew and English)
            if (query_lower in book.get('author', '').lower() or 
                query_lower in book.get('authorEnglish', '').lower()):
                match = True
            
            # Filter by category if specified
            if category and category_lower not in book.get('categoryEnglish', '').lower():
                match = False
            
            # Filter by author if specified
            if author and (author_lower not in book.get('author', '').lower() and 
                          author_lower not in book.get('authorEnglish', '').lower()):
                match = False
            
            if match:
                filtered_books.append(book)
                if len(filtered_books) >= limit:
                    break
        
        return filtered_books
    
    async def get_book_categories(self) -> List[Dict]:
        """Get all unique categories from the library"""
        books = await self.get_books_library()
        categories = {}
        
        for book in books:
            cat_en = book.get('categoryEnglish', '')
            cat_he = book.get('category', '')
            if cat_en and cat_en not in categories:
                categories[cat_en] = {
                    'english': cat_en,
                    'hebrew': cat_he,
                    'count': 1
                }
            elif cat_en in categories:
                categories[cat_en]['count'] += 1
        
        return list(categories.values())
    
    async def get_random_book(self, category: str = "") -> Optional[Dict]:
        """Get a random book from the library"""
        books = await self.get_books_library()
        
        if category:
            category_lower = category.lower()
            filtered_books = [
                book for book in books 
                if category_lower in book.get('categoryEnglish', '').lower()
            ]
            books = filtered_books
        
        if books:
            return random.choice(books)
        return None
    
    async def get_chassidic_books(self, limit: int = 10) -> List[Dict]:
        """Get Chassidic/Hasidic books specifically"""
        return await self.search_books("", category="Sifrei Chasidut", limit=limit)
    
    async def get_responsa_books(self, limit: int = 10) -> List[Dict]:
        """Get Responsa (Sheelot u'Teshuvot) books"""
        return await self.search_books("", category="Responsa", limit=limit)
    
    async def get_talmud_commentaries(self, limit: int = 10) -> List[Dict]:
        """Get Talmud commentary books"""
        return await self.search_books("", category="Acharonim on Talmud Bavli", limit=limit)
    
    async def get_biblical_commentaries(self, limit: int = 10) -> List[Dict]:
        """Get biblical commentary books"""
        categories = ["Bible Commentary", "Biblical Commentary"]
        all_books = []
        for category in categories:
            books = await self.search_books("", category=category, limit=limit)
            all_books.extend(books)
        return all_books[:limit]
    
    async def get_halachic_books(self, limit: int = 10) -> List[Dict]:
        """Get Halachic (Jewish law) books"""
        categories = ["Commentaries on Shulchan Aruch", "Halakhah"]
        all_books = []
        for category in categories:
            books = await self.search_books("", category=category, limit=limit)
            all_books.extend(books)
        return all_books[:limit]
    
    async def get_books_by_author(self, author: str, limit: int = 10) -> List[Dict]:
        """Get books by a specific author"""
        return await self.search_books("", author=author, limit=limit)
    
    async def get_books_by_period(self, min_year: int = 1800, max_year: int = 2000, limit: int = 10) -> List[Dict]:
        """Get books from a specific time period"""
        books = await self.get_books_library()
        
        filtered_books = []
        for book in books:
            year = book.get('printYear', 0)
            if isinstance(year, int) and min_year <= year <= max_year:
                filtered_books.append(book)
                if len(filtered_books) >= limit:
                    break
        
        return filtered_books
    
    async def get_library_statistics(self) -> Dict:
        """Get statistics about the Dicta library"""
        books = await self.get_books_library()
        categories = await self.get_book_categories()
        
        # Calculate statistics
        total_books = len(books)
        authors = set()
        years = []
        locations = set()
        
        for book in books:
            if book.get('authorEnglish'):
                authors.add(book['authorEnglish'])
            if book.get('printYear') and isinstance(book['printYear'], int):
                years.append(book['printYear'])
            if book.get('printLocationEnglish'):
                locations.add(book['printLocationEnglish'])
        
        stats = {
            'total_books': total_books,
            'total_categories': len(categories),
            'total_authors': len(authors),
            'total_locations': len(locations),
            'year_range': {
                'earliest': min(years) if years else 0,
                'latest': max(years) if years else 0
            },
            'categories': categories[:10]  # Top 10 categories
        }
        
        return stats
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()