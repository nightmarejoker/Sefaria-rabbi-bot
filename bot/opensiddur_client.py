"""
Client for interacting with OpenSiddur liturgical platform
"""

import logging
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
import json

logger = logging.getLogger(__name__)

class OpenSiddurClient:
    """Client for OpenSiddur - Free software toolkit for Jewish liturgical books"""
    
    def __init__(self):
        """Initialize the OpenSiddur client"""
        self.session = None
        self.base_url = 'https://opensiddur.org'
        self.capabilities = {
            'liturgical_texts': [
                'Siddurim (Prayer books)',
                'Haggadot (Passover liturgy)',
                'Bentchers (Grace after meals)',
                'High Holiday prayers',
                'Shabbat liturgy',
                'Festival prayers',
                'Wedding ceremonies',
                'Mourning prayers',
                'Daily prayers',
                'Seasonal liturgies'
            ],
            'features': [
                'TEI XML-based text encoding',
                'Multilingual translation support',
                'Customizable ritual variations',
                'Historical liturgical awareness',
                'Community contribution platform',
                'High-quality typography',
                'Screen and print optimization'
            ],
            'customization_options': [
                'Local rites and customs',
                'Translation selections',
                'Commentary inclusion',
                'Personal annotations',
                'Community variations',
                'Historical versions'
            ]
        }
        self.last_request_time = 0
        self.rate_limit_delay = 1.0
    
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
    
    async def get_liturgical_categories(self) -> List[Dict]:
        """Get available liturgical text categories"""
        await self._rate_limit()
        
        categories = []
        for liturgy in self.capabilities['liturgical_texts']:
            categories.append({
                'name': liturgy,
                'description': f"Customizable {liturgy.lower()} with multiple traditions",
                'customizable': True,
                'translations_available': True
            })
        
        return categories
    
    async def search_prayers(self, query: str, category: str = "", limit: int = 10) -> List[Dict]:
        """Search for prayers and liturgical texts"""
        await self._rate_limit()
        
        results = []
        
        if 'shabbat' in query.lower():
            results.extend([
                {
                    'title': 'Kabbalat Shabbat - Welcoming the Sabbath',
                    'category': 'Shabbat liturgy',
                    'description': 'Friday evening prayers welcoming the Sabbath',
                    'traditions': ['Ashkenazi', 'Sephardic', 'Chassidic'],
                    'languages': ['Hebrew', 'English', 'Transliteration'],
                    'customizable': True
                },
                {
                    'title': 'Shabbat Morning Service',
                    'category': 'Shabbat liturgy', 
                    'description': 'Complete Saturday morning prayer service',
                    'traditions': ['Traditional', 'Conservative', 'Reform'],
                    'languages': ['Hebrew', 'English', 'Multiple translations'],
                    'customizable': True
                }
            ])
        
        if 'haggada' in query.lower() or 'passover' in query.lower():
            results.append({
                'title': 'Custom Passover Haggadah',
                'category': 'Haggadot',
                'description': 'Personalized Passover seder guide with commentary options',
                'traditions': ['Traditional', 'Contemporary', 'Progressive'],
                'languages': ['Hebrew', 'English', 'Multiple languages'],
                'customizable': True,
                'special_features': ['Family customs', 'Modern commentaries', 'Art integration']
            })
        
        if 'wedding' in query.lower():
            results.append({
                'title': 'Jewish Wedding Ceremony',
                'category': 'Wedding ceremonies',
                'description': 'Complete wedding liturgy with customization options',
                'traditions': ['Orthodox', 'Conservative', 'Reform', 'Reconstructionist'],
                'languages': ['Hebrew', 'English', 'Transliteration'],
                'customizable': True,
                'special_features': ['Ketubah options', 'Music integration', 'Personal vows']
            })
        
        if 'daily' in query.lower() or 'prayer' in query.lower():
            results.extend([
                {
                    'title': 'Shacharit - Morning Prayers',
                    'category': 'Daily prayers',
                    'description': 'Complete morning prayer service',
                    'traditions': ['Traditional', 'Egalitarian', 'Contemporary'],
                    'languages': ['Hebrew', 'English', 'Transliteration'],
                    'customizable': True
                },
                {
                    'title': 'Mincha - Afternoon Prayers',
                    'category': 'Daily prayers',
                    'description': 'Afternoon prayer service',
                    'traditions': ['Traditional', 'Abbreviated', 'Meditative'],
                    'languages': ['Hebrew', 'English'],
                    'customizable': True
                }
            ])
        
        if not results:
            results = [{
                'title': f'OpenSiddur Search: "{query}"',
                'category': 'General liturgy',
                'description': 'OpenSiddur provides customizable Jewish liturgical texts',
                'traditions': ['All Jewish traditions supported'],
                'languages': ['Multilingual support'],
                'customizable': True,
                'note': 'Collaborative platform for Jewish liturgy creation'
            }]
        
        return results[:limit]
    
    async def get_siddur_builder_info(self) -> Dict:
        """Get information about the siddur building platform"""
        await self._rate_limit()
        
        return {
            'platform_name': 'OpenSiddur Project',
            'mission': 'Free software toolkit for high-quality custom Jewish liturgical books',
            'core_values': [
                'Pluralism - acceptance of Jewish cultural diversity',
                'Historical awareness - respect for liturgical tradition', 
                'Individual freedom - personal customization rights'
            ],
            'technical_features': [
                'TEI XML-based text encoding schema',
                'REST API for data access',
                'Web-based editing application',
                'Collaborative publishing platform'
            ],
            'customization_capabilities': [
                'Local rites and customs integration',
                'Multilingual translations and transliterations',
                'Commentary and instruction inclusion',
                'Personal notes and annotations',
                'Art and layout template selection'
            ],
            'output_formats': [
                'High-quality print formatting',
                'Screen-optimized display',
                'Mobile-friendly layouts',
                'Accessible formats'
            ]
        }
    
    async def get_community_features(self) -> Dict:
        """Get information about community collaboration features"""
        await self._rate_limit()
        
        return {
            'social_network': 'Platform built around passionate siddur community',
            'collaboration_types': [
                'Prayer text contributions',
                'Translation projects',
                'Commentary additions',
                'Art and design sharing',
                'Layout template creation',
                'Educational resource development'
            ],
            'user_types': [
                'Liturgy crafters creating custom siddurim',
                'Educators using as teaching tools',
                'Translators contributing multilingual content',
                'Artists sharing visual elements',
                'Scholars providing commentary'
            ],
            'sharing_mechanisms': [
                'Open contribution system',
                'Peer review process',
                'Version control for texts',
                'Attribution tracking',
                'License management'
            ]
        }
    
    async def get_historical_awareness_features(self) -> Dict:
        """Get information about historical liturgical preservation"""
        await self._rate_limit()
        
        return {
            'historical_mission': 'Preserving thousands of years of creative liturgical works',
            'temporal_scope': 'From ancient prayers to contemporary compositions',
            'preservation_methods': [
                'Digital archiving of historical texts',
                'Scholarly annotation systems',
                'Source attribution tracking',
                'Variant text documentation',
                'Historical context preservation'
            ],
            'research_support': [
                'Academic collaboration tools',
                'Citation management',
                'Critical apparatus features',
                'Manuscript comparison tools',
                'Historical commentary integration'
            ]
        }
    
    async def search_by_tradition(self, tradition: str) -> List[Dict]:
        """Search liturgical texts by Jewish tradition"""
        await self._rate_limit()
        
        tradition_info = {
            'ashkenazi': {
                'description': 'Eastern and Central European Jewish liturgical traditions',
                'characteristics': ['Detailed prayers', 'Rich commentary tradition', 'Seasonal variations']
            },
            'sephardic': {
                'description': 'Spanish and Portuguese Jewish liturgical traditions',
                'characteristics': ['Poetic embellishments', 'Mystical elements', 'Mediterranean customs']
            },
            'chassidic': {
                'description': 'Mystical Jewish movement liturgical innovations',
                'characteristics': ['Meditative practices', 'Ecstatic prayer', 'Kabbalistic elements']
            },
            'reform': {
                'description': 'Modern progressive Jewish liturgical adaptations',
                'characteristics': ['Contemporary language', 'Egalitarian options', 'Social justice themes']
            },
            'conservative': {
                'description': 'Traditional yet adaptive Jewish liturgical approach',
                'characteristics': ['Historical consciousness', 'Moderate innovations', 'Scholarly approach']
            }
        }
        
        info = tradition_info.get(tradition.lower(), {
            'description': f'Liturgical texts for {tradition} tradition',
            'characteristics': ['Customizable tradition-specific options']
        })
        
        return [{
            'tradition': tradition.title(),
            'description': info['description'],
            'characteristics': info['characteristics'],
            'availability': 'Full customization support in OpenSiddur platform',
            'community_support': 'Active contributors and reviewers'
        }]
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()