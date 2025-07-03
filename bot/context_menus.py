"""
Context menu commands for enhanced user interaction - following discord.py best practices
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class ContextMenus(commands.Cog):
    """Context menu commands for right-click interactions"""
    
    def __init__(self, bot, sefaria_client):
        self.bot = bot
        self.sefaria_client = sefaria_client
    
    @app_commands.context_menu(name='Search Sefaria')
    async def search_sefaria_context(self, interaction: discord.Interaction, message: discord.Message):
        """Search Sefaria for text in a message via right-click context menu"""
        if not message.content.strip():
            await interaction.response.send_message(
                "❌ No searchable text found in this message.", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Extract first 100 characters for search
            search_text = message.content.strip()[:100]
            
            # Search Sefaria
            results = await self.sefaria_client.search_texts(search_text, limit=3)
            
            if not results:
                embed = discord.Embed(
                    title="🔍 Sefaria Search Results",
                    description=f"No results found for: *{search_text}*",
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title="🔍 Sefaria Search Results",
                    description=f"Results for: *{search_text}*",
                    color=discord.Color.blue()
                )
                
                for i, result in enumerate(results[:3], 1):
                    text_snippet = result.get('text', 'No text available')
                    if len(text_snippet) > 100:
                        text_snippet = text_snippet[:100] + "..."
                    
                    embed.add_field(
                        name=f"{i}. {result.get('ref', 'Unknown Reference')}",
                        value=text_snippet,
                        inline=False
                    )
            
            embed.set_footer(text="Use /search for more detailed searches")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in search_sefaria_context: {e}")
            await interaction.followup.send(
                "❌ Error searching Sefaria. Please try again.", 
                ephemeral=True
            )
    
    @app_commands.context_menu(name='Get Hebrew Date')
    async def hebrew_date_context(self, interaction: discord.Interaction, message: discord.Message):
        """Get Hebrew date for when the message was sent"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from datetime import datetime
            
            # Get message timestamp
            message_date = message.created_at.date()
            
            embed = discord.Embed(
                title="📅 Hebrew Date Information",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="📅 Gregorian Date",
                value=message_date.strftime("%B %d, %Y"),
                inline=True
            )
            
            # This would require Hebrew date conversion - simplified for now
            embed.add_field(
                name="📜 Hebrew Date",
                value="Contact administrator for Hebrew date conversion",
                inline=True
            )
            
            embed.add_field(
                name="🕐 Time Sent",
                value=discord.utils.format_dt(message.created_at, "f"),
                inline=False
            )
            
            embed.set_footer(text="Use /hebrewdate for today's Hebrew date")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in hebrew_date_context: {e}")
            await interaction.followup.send(
                "❌ Error getting Hebrew date information.", 
                ephemeral=True
            )

async def setup(bot):
    """Setup function for loading the cog"""
    sefaria_client = getattr(bot, 'sefaria_client', None)
    if sefaria_client:
        await bot.add_cog(ContextMenus(bot, sefaria_client))
    else:
        logger.warning("Sefaria client not found, skipping context menus")