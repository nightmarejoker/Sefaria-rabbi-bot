"""
Utility functions for formatting and processing text
"""
import discord
import re
from typing import Dict, Optional

def format_text_response(text_data: Dict, language: Optional[str] = "both") -> discord.Embed:
    """Format text data into a Discord embed"""
    # Extract basic information
    title = text_data.get('title', 'Unknown Text')
    ref = text_data.get('ref', title)
    
    # Get text content
    english_text = ""
    hebrew_text = ""
    
    # Handle different text formats
    if 'text' in text_data:
        if isinstance(text_data['text'], list):
            english_text = " ".join(text_data['text']) if text_data['text'] else ""
        else:
            english_text = str(text_data['text'])
    
    if 'he' in text_data:
        if isinstance(text_data['he'], list):
            hebrew_text = " ".join(text_data['he']) if text_data['he'] else ""
        else:
            hebrew_text = str(text_data['he'])
    
    # Clean up HTML tags
    english_text = clean_html(english_text)
    hebrew_text = clean_html(hebrew_text)
    
    # Create embed
    embed = discord.Embed(
        title=title,
        color=discord.Color.blue()
    )
    
    # Check if text was truncated
    truncated_note = ""
    if text_data.get('truncated'):
        truncated_note = "\n\n*Note: Text has been shortened for readability. Use a specific verse reference for complete passages.*"
    
    # Add text based on language preference
    language = (language or "both").lower()
    if language == "english" and english_text:
        embed.description = truncate_text(english_text, 2000) + truncated_note
    elif language == "hebrew" and hebrew_text:
        embed.description = truncate_text(hebrew_text, 2000) + truncated_note
    elif language == "both":
        content_parts = []
        
        if hebrew_text:
            content_parts.append(f"**Hebrew:**\n{truncate_text(hebrew_text, 900)}")
        
        if english_text:
            content_parts.append(f"**English:**\n{truncate_text(english_text, 900)}")
        
        if content_parts:
            embed.description = "\n\n".join(content_parts) + truncated_note
        else:
            embed.description = "No text content available."
    else:
        embed.description = "No text available for the requested language."
    
    # Add source information
    if 'url' in text_data:
        embed.add_field(
            name="📖 Source",
            value=f"[{ref}]({text_data['url']})",
            inline=False
        )
    else:
        embed.add_field(
            name="📖 Reference",
            value=ref,
            inline=False
        )
    
    # Add categories if available
    if 'categories' in text_data and text_data['categories']:
        categories = text_data['categories']
        if isinstance(categories, list):
            embed.add_field(
                name="🏷️ Categories",
                value=" > ".join(categories),
                inline=False
            )
    
    # Add author information if available
    if 'authors' in text_data and text_data['authors']:
        authors = text_data['authors']
        if isinstance(authors, list):
            embed.add_field(
                name="✍️ Authors",
                value=", ".join(authors),
                inline=True
            )
    
    # Add composition date if available
    if 'compDate' in text_data:
        comp_date = text_data['compDate']
        if comp_date:
            embed.add_field(
                name="📅 Composed",
                value=str(comp_date),
                inline=True
            )
    
    # Set footer
    embed.set_footer(
        text="Powered by Sefaria • sefaria.org",
        icon_url="https://www.sefaria.org/static/img/logo.png"
    )
    
    return embed

def clean_html(text: str) -> str:
    """Remove HTML tags and clean up text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Replace HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def truncate_text(text: str, max_length: int = 2000) -> str:
    """Truncate text to fit Discord message limits"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Try to truncate at sentence boundary
    truncated = text[:max_length]
    last_sentence = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_sentence > max_length * 0.7:  # If we found a sentence boundary in the last 30%
        truncated = truncated[:last_sentence + 1]
    else:
        # Truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # If we found a space in the last 20%
            truncated = truncated[:last_space]
        else:
            truncated = truncated[:max_length - 3]
    
    return truncated + "..."

def format_reference(ref: str) -> str:
    """Format a text reference for display"""
    # Basic formatting - could be expanded
    return ref.replace('_', ' ').title()

def is_hebrew(text: str) -> bool:
    """Check if text contains Hebrew characters"""
    if not text:
        return False
    
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
    return bool(hebrew_pattern.search(text))

def extract_verses(text_data: Dict) -> list:
    """Extract individual verses from text data"""
    verses = []
    
    if 'text' in text_data and isinstance(text_data['text'], list):
        for i, verse in enumerate(text_data['text'], 1):
            if verse:  # Skip empty verses
                verses.append({
                    'number': i,
                    'english': clean_html(verse),
                    'hebrew': ''
                })
    
    if 'he' in text_data and isinstance(text_data['he'], list):
        for i, verse in enumerate(text_data['he'], 1):
            if verse and i <= len(verses):  # Skip empty verses and match with English
                verses[i-1]['hebrew'] = clean_html(verse)
    
    return verses
