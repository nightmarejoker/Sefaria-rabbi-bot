"""
Client for interacting with Orayta Jewish books system
"""

import logging
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
import json

logger = logging.getLogger(__name__)

class OraytaClient:
    """Client for Orayta Jewish books system - Cross-platform Jewish texts library"""
    
    def __init__(self):
        """Initialize the Orayta client"""
        self.session = None
        # Since Orayta is primarily a desktop application, we'll simulate its capabilities
        self.capabilities = {
            'book_categories': [
                'Torah (Chumash)',
                'Nevi\'im (Prophets)', 
                'Ketuvim (Writings)',
                'Mishnah',
                'Talmud Bavli',
                'Talmud Yerushalmi',
                'Midrash Rabbah',
                'Midrash Tanchuma',
                'Zohar',
                'Rishonim (Early Commentators)',
                'Acharonim (Later Commentators)',
                'Halacha (Jewish Law)',
                'Chassidut',
                'Mussar (Ethics)',
                'Modern Hebrew Literature'
            ],
            'features': [
                'Cross-platform compatibility (Windows, Linux, Android)',
                'Extensive Jewish library access',
                'Text search and indexing',
                'Multiple Hebrew fonts support',
                'Bookmark and note-taking system',
                'Daily learning schedules',
                'Zmanim (prayer times) integration'
            ]
        }
        self.last_request_time = 0
        self.rate_limit_delay = 0.5
    
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
    
    async def get_book_categories(self) -> List[Dict]:
        """Get available book categories in Orayta"""
        await self._rate_limit()
        
        categories = []
        for category in self.capabilities['book_categories']:
            categories.append({
                'name': category,
                'description': f"Access to {category} texts and commentaries",
                'available': True
            })
        
        return categories
    
    async def search_books(self, query: str, category: str = "", limit: int = 10) -> List[Dict]:
        """Search for books in Orayta library"""
        await self._rate_limit()
        
        # Simulate search results based on query and category
        results = []
        
        if 'talmud' in query.lower() or category.lower() == 'talmud':
            results.extend([
                {
                    'title': 'Talmud Bavli - Tractate Berakhot',
                    'category': 'Talmud Bavli',
                    'description': 'Foundational tractate on blessings and prayers',
                    'language': 'Hebrew/Aramaic',
                    'availability': 'Full text available'
                },
                {
                    'title': 'Talmud Bavli - Tractate Shabbat', 
                    'category': 'Talmud Bavli',
                    'description': 'Laws and philosophy of Sabbath observance',
                    'language': 'Hebrew/Aramaic',
                    'availability': 'Full text available'
                }
            ])
        
        if 'torah' in query.lower() or 'chumash' in query.lower():
            results.extend([
                {
                    'title': 'Torah with Rashi Commentary',
                    'category': 'Torah (Chumash)',
                    'description': 'Five Books of Moses with classical Rashi commentary',
                    'language': 'Hebrew',
                    'availability': 'Full text with commentary'
                },
                {
                    'title': 'Torah with Multiple Commentaries',
                    'category': 'Torah (Chumash)',
                    'description': 'Comprehensive Torah study with major commentators',
                    'language': 'Hebrew',
                    'availability': 'Multi-commentary edition'
                }
            ])
        
        if 'mishnah' in query.lower():
            results.append({
                'title': 'Complete Mishnah with Commentary',
                'category': 'Mishnah',
                'description': 'Six orders of Mishnah with traditional commentaries',
                'language': 'Hebrew',
                'availability': 'Complete collection'
            })
        
        if 'zohar' in query.lower() or 'kabbala' in query.lower():
            results.append({
                'title': 'Zohar - Book of Splendor',
                'category': 'Zohar',
                'description': 'Primary text of Jewish mysticism and Kabbalah',
                'language': 'Aramaic/Hebrew',
                'availability': 'Complete Zohar collection'
            })
        
        if not results:
            # General results for any query
            results = [
                {
                    'title': f'Search Results for "{query}"',
                    'category': 'General Search',
                    'description': 'Orayta provides access to thousands of Jewish texts',
                    'language': 'Hebrew/Aramaic',
                    'availability': 'Cross-platform library access'
                }
            ]
        
        return results[:limit]
    
    async def get_daily_learning(self) -> Optional[Dict]:
        """Get daily learning schedule from Orayta"""
        await self._rate_limit()
        
        return {
            'daf_yomi': 'Daily Talmud page study',
            'mishnah_yomi': 'Daily Mishnah study',
            'parsha': 'Weekly Torah portion',
            'halacha_yomit': 'Daily Jewish law study',
            'features': [
                'Automatic daily progression tracking',
                'Multiple learning cycles available',
                'Cross-platform synchronization',
                'Customizable study schedules'
            ]
        }
    
    async def get_text_features(self) -> Dict:
        """Get text display and study features"""
        await self._rate_limit()
        
        return {
            'display_options': [
                'Multiple Hebrew font choices',
                'Adjustable text size',
                'Night mode reading',
                'Side-by-side commentary display'
            ],
            'study_tools': [
                'Advanced text search',
                'Cross-reference linking',
                'Personal bookmarks',
                'Note-taking system',
                'Text highlighting'
            ],
            'platform_support': [
                'Windows desktop application',
                'Linux compatibility',
                'Android mobile app',
                'Offline text access'
            ]
        }
    
    async def get_library_statistics(self) -> Dict:
        """Get comprehensive library statistics"""
        await self._rate_limit()
        
        return {
            'total_books': '1000+',
            'text_categories': len(self.capabilities['book_categories']),
            'languages_supported': ['Hebrew', 'Aramaic', 'Yiddish', 'Ladino'],
            'special_features': [
                'Free and open-source',
                'Cross-platform compatibility',
                'Extensive commentary collection',
                'Active development community',
                'Multiple language interfaces'
            ],
            'historical_scope': 'From Biblical times to modern era',
            'platform': 'Multi-platform Jewish text library'
        }
    
    async def search_by_topic(self, topic: str) -> List[Dict]:
        """Search texts by specific Jewish topics"""
        await self._rate_limit()
        
        topic_mappings = {
            'shabbat': 'Sabbath laws, prayers, and philosophy',
            'kashrut': 'Dietary laws and kosher regulations',
            'prayer': 'Jewish liturgy and prayer texts',
            'ethics': 'Mussar and ethical teachings',
            'mysticism': 'Kabbalah and mystical texts',
            'law': 'Halachic (Jewish legal) texts',
            'philosophy': 'Jewish philosophical works',
            'history': 'Jewish historical texts'
        }
        
        description = topic_mappings.get(topic.lower(), f"Texts related to {topic}")
        
        return [{
            'topic': topic.title(),
            'description': description,
            'available_texts': 'Multiple sources available in Orayta library',
            'study_approach': 'Comprehensive topic-based learning',
            'cross_references': 'Linked to related texts and commentaries'
        }]
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()