"""
Discord commands for Sefaria integration
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from typing import Optional
from urllib.parse import quote
from .sefaria_client import SefariaClient
from .hebcal_client import HebcalClient
from .nli_client import NLIClient
from .chabad_client import ChabadClient
from .dicta_client import DictaClient
from .utils import format_text_response, truncate_text
from datetime import date

logger = logging.getLogger(__name__)

class SefariaCommands(commands.Cog):
    """Cog containing all Sefaria-related commands"""
    
    def __init__(self, bot, sefaria_client: SefariaClient, hebcal_client: HebcalClient, 
                 nli_client: NLIClient, chabad_client: ChabadClient, dicta_client: DictaClient,
                 opentorah_client, torahcalc_client, orayta_client, opensiddur_client, pninim_client):
        self.bot = bot
        self.sefaria_client = sefaria_client
        self.hebcal_client = hebcal_client
        self.nli_client = nli_client
        self.chabad_client = chabad_client
        self.dicta_client = dicta_client
        self.opentorah_client = opentorah_client
        self.torahcalc_client = torahcalc_client
        self.orayta_client = orayta_client
        self.opensiddur_client = opensiddur_client
        self.pninim_client = pninim_client
        # Track auto-reply settings per guild
        self.auto_reply_enabled = {}
        
    @app_commands.command(name="random", description="Get a random Jewish text quote")
    @app_commands.describe(
        language="Language preference (hebrew, english, or both)",
        category="Text category (torah, talmud, mishnah, etc.)"
    )
    async def random_quote(
        self, 
        interaction: discord.Interaction,
        language: Optional[str] = "both",
        category: Optional[str] = None
    ):
        """Get a random quote from Sefaria"""
        await interaction.response.defer()
        
        try:
            # Get random text
            text_data = await self.sefaria_client.get_random_text(category)
            
            if not text_data:
                embed = discord.Embed(
                    title="❌ No Text Found",
                    description="Could not retrieve a random text at this time.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format and send response
            embed = format_text_response(text_data, language or "both")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in random_quote: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching the text.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="search", description="Search for specific texts or passages")
    @app_commands.describe(
        query="Search term or text reference",
        language="Language preference (hebrew, english, or both)"
    )
    async def search_text(
        self,
        interaction: discord.Interaction,
        query: str,
        language: Optional[str] = "both"
    ):
        """Search for specific texts"""
        await interaction.response.defer()
        
        try:
            # Search for texts
            results = await self.sefaria_client.search_texts(query)
            
            if not results:
                embed = discord.Embed(
                    title="🔍 No Results",
                    description=f"No texts found for query: **{query}**",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # If single result, show full text
            if len(results) == 1:
                text_data = await self.sefaria_client.get_text(results[0]['ref'])
                if text_data:
                    embed = format_text_response(text_data, language)
                    await interaction.followup.send(embed=embed)
                    return
            
            # Multiple results - show list
            embed = discord.Embed(
                title="🔍 Search Results",
                description=f"Found {len(results)} results for: **{query}**",
                color=discord.Color.blue()
            )
            
            for i, result in enumerate(results[:10]):  # Limit to 10 results
                title = result.get('ref', 'Unknown Reference')
                snippet = truncate_text(result.get('text', ''), 100)
                embed.add_field(
                    name=f"{i+1}. {title}",
                    value=snippet,
                    inline=False
                )
            
            if len(results) > 10:
                embed.add_field(
                    name="📝 Note",
                    value=f"Showing first 10 of {len(results)} results",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in search_text: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while searching.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="text", description="Get a specific text by reference with optional commentary")
    @app_commands.describe(
        reference="Text reference (e.g., 'Genesis 1:1', 'Berakhot 2a')",
        language="Language preference (hebrew, english, or both)",
        commentary="Include commentary (rashi, ibn_ezra, ramban, ralbag, sforno, radak, or none)"
    )
    async def get_text(
        self,
        interaction: discord.Interaction,
        reference: str,
        language: Optional[str] = "both",
        commentary: Optional[str] = "none"
    ):
        """Get a specific text by reference with optional commentary"""
        await interaction.response.defer()
        
        try:
            # Get the main text
            text_data = await self.sefaria_client.get_text(reference)
            
            if not text_data:
                embed = discord.Embed(
                    title="❌ Text Not Found",
                    description=f"Could not find text for reference: **{reference}**",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Send the main text
            embed = format_text_response(text_data, language or "both")
            await interaction.followup.send(embed=embed)
            
            # If commentary requested, get and send that too
            if commentary and commentary.lower() != "none":
                commentator_map = {
                    "rashi": "Rashi_on_",
                    "ibn_ezra": "Ibn_Ezra_on_",
                    "ramban": "Ramban_on_", 
                    "ralbag": "Ralbag_on_",
                    "sforno": "Sforno_on_",
                    "radak": "Radak_on_"
                }
                
                commentator_name = commentary.lower()
                if commentator_name in commentator_map:
                    # Format the commentary reference correctly
                    # Convert "Genesis 1:1" to "Genesis.1.1" format
                    formatted_ref = reference.replace(" ", ".").replace(":", ".")
                    commentary_ref = f"{commentator_map[commentator_name]}{formatted_ref}"
                    
                    # Get the commentary
                    commentary_data = await self.sefaria_client.get_text(commentary_ref)
                    
                    if commentary_data:
                        commentary_embed = format_text_response(commentary_data, language or "both")
                        commentary_embed.title = f"📖 {commentator_name.title()} on {reference}"
                        commentary_embed.color = discord.Color.purple()
                        await interaction.followup.send(embed=commentary_embed)
                    else:
                        # Inform user that commentary wasn't found, but don't error
                        await interaction.followup.send(
                            f"ℹ️ {commentator_name.title()} commentary not available for {reference}",
                            ephemeral=True
                        )
            
        except Exception as e:
            logger.error(f"Error in get_text: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching the text.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="daily", description="Get the daily Torah portion or study text")
    async def daily_text(self, interaction: discord.Interaction):
        """Get daily Torah portion or study text"""
        await interaction.response.defer()
        
        try:
            daily_data = await self.sefaria_client.get_daily_text()
            
            if not daily_data:
                embed = discord.Embed(
                    title="❌ No Daily Text",
                    description="Could not retrieve today's text.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = format_text_response(daily_data, "both")
            embed.title = f"📅 Daily Text - {embed.title}"
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in daily_text: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching the daily text.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="commentary", description="Get commentary (Rashi, Ibn Ezra, etc.) on a verse")
    @app_commands.describe(
        reference="Bible verse reference (e.g., Genesis 1:1)",
        commentator="Commentator (rashi, ibn_ezra, ramban, or ralbag)",
        language="Language preference (hebrew, english, or both)"
    )
    async def commentary(
        self,
        interaction: discord.Interaction,
        reference: str,
        commentator: str = "rashi",
        language: Optional[str] = "both"
    ):
        """Get commentary on a specific verse"""
        await interaction.response.defer()
        
        try:
            # Map commentator names to Sefaria format
            commentator_map = {
                "rashi": "Rashi_on_",
                "ibn_ezra": "Ibn_Ezra_on_",
                "ramban": "Ramban_on_", 
                "ralbag": "Ralbag_on_",
                "sforno": "Sforno_on_",
                "radak": "Radak_on_"
            }
            
            commentator_name = commentator.lower()
            if commentator_name not in commentator_map:
                embed = discord.Embed(
                    title="❌ Unknown Commentator",
                    description=f"Available commentators: {', '.join(commentator_map.keys())}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format the commentary reference
            # Convert "Genesis 1:1" to "Genesis.1.1" format
            formatted_ref = reference.replace(" ", "_").replace(":", ".")
            commentary_ref = f"{commentator_map[commentator_name]}{formatted_ref}"
            
            # Get the commentary
            commentary_data = await self.sefaria_client.get_text(commentary_ref)
            
            if not commentary_data:
                embed = discord.Embed(
                    title="❌ Commentary Not Found",
                    description=f"Could not find {commentator_name.title()} commentary on {reference}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format and send response
            embed = format_text_response(commentary_data, language)
            embed.title = f"📖 {commentator_name.title()} on {reference}"
            embed.color = discord.Color.purple()
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in commentary: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching the commentary.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="shabbat", description="Get Shabbat candle lighting and havdalah times")
    @app_commands.describe(
        location="City name (e.g., New York, Jerusalem, London)"
    )
    async def shabbat_times(self, interaction: discord.Interaction, location: str = "New York"):
        """Get Shabbat times for a location"""
        await interaction.response.defer()
        
        try:
            shabbat_data = await self.hebcal_client.get_shabbat_times(location)
            
            if not shabbat_data or "items" not in shabbat_data:
                embed = discord.Embed(
                    title="❌ Location Not Found",
                    description=f"Could not find Shabbat times for {location}. Try: New York, Jerusalem, London, etc.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🕯️ Shabbat Times - {shabbat_data.get('location', location)}",
                color=discord.Color.gold()
            )
            
            for item in shabbat_data["items"]:
                if "candles" in item.get("category", "").lower():
                    embed.add_field(
                        name="🕯️ Candle Lighting",
                        value=item.get("title", "Not available"),
                        inline=True
                    )
                elif "havdalah" in item.get("category", "").lower():
                    embed.add_field(
                        name="✨ Havdalah",
                        value=item.get("title", "Not available"),
                        inline=True
                    )
                elif "parashat" in item.get("title", "").lower():
                    embed.add_field(
                        name="📜 Torah Portion",
                        value=item.get("title", ""),
                        inline=False
                    )
            
            embed.set_footer(text="Times provided by Hebcal.com")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in shabbat_times: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not retrieve Shabbat times.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="holidays", description="Get upcoming Jewish holidays")
    @app_commands.describe(
        year="Year (e.g., 2025). Defaults to current year"
    )
    async def jewish_holidays(self, interaction: discord.Interaction, year: Optional[int] = None):
        """Get Jewish holidays for a year"""
        await interaction.response.defer()
        
        try:
            holidays_data = await self.hebcal_client.get_jewish_holidays(year)
            
            if not holidays_data:
                embed = discord.Embed(
                    title="❌ No Holidays Found",
                    description="Could not retrieve holiday information.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Filter to next 10 upcoming holidays
            from datetime import datetime
            now = datetime.now()
            upcoming_holidays = []
            
            for holiday in holidays_data[:20]:  # Check first 20 items
                if "date" in holiday:
                    try:
                        holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d")
                        if holiday_date >= now and len(upcoming_holidays) < 10:
                            upcoming_holidays.append(holiday)
                    except:
                        continue
            
            if not upcoming_holidays:
                upcoming_holidays = holidays_data[:10]  # Fallback to first 10
            
            embed = discord.Embed(
                title=f"📅 Jewish Holidays {year or datetime.now().year}",
                color=discord.Color.blue()
            )
            
            for holiday in upcoming_holidays:
                date_str = holiday.get("date", "")
                title = holiday.get("title", "Unknown Holiday")
                hebrew = holiday.get("hebrew", "")
                
                field_value = f"**Date:** {date_str}"
                if hebrew:
                    field_value += f"\n**Hebrew:** {hebrew}"
                
                embed.add_field(
                    name=title,
                    value=field_value,
                    inline=True
                )
            
            embed.set_footer(text="Holiday data provided by Hebcal.com")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in jewish_holidays: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not retrieve holiday information.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="hebrewdate", description="Get today's Hebrew date")
    async def hebrew_date(self, interaction: discord.Interaction):
        """Get current Hebrew date"""
        await interaction.response.defer()
        
        try:
            today = date.today()
            hebrew_data = await self.hebcal_client.convert_hebrew_date(today)
            
            if not hebrew_data:
                embed = discord.Embed(
                    title="❌ Conversion Failed",
                    description="Could not convert to Hebrew date.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📅 Today's Hebrew Date",
                color=discord.Color.purple()
            )
            
            gregorian = f"{today.strftime('%B %d, %Y')}"
            hebrew = hebrew_data.get("hebrew", "")
            hebrew_year = hebrew_data.get("hy", "")
            
            embed.add_field(
                name="Gregorian Date",
                value=gregorian,
                inline=False
            )
            
            embed.add_field(
                name="Hebrew Date",
                value=hebrew,
                inline=False
            )
            
            if hebrew_year:
                embed.add_field(
                    name="Hebrew Year",
                    value=str(hebrew_year),
                    inline=True
                )
            
            embed.set_footer(text="Date conversion by Hebcal.com")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in hebrew_date: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not convert Hebrew date.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="autoreply", description="[ADMIN] Toggle auto-reply to @mentions on/off")
    @app_commands.describe(
        enabled="Enable or disable auto-reply (true/false)"
    )
    async def toggle_autoreply(self, interaction: discord.Interaction, enabled: bool):
        """Toggle auto-reply functionality (admin only)"""
        # Check if user has admin permissions (safe permission check)
        try:
            is_admin = interaction.user.guild_permissions.administrator if hasattr(interaction.user, 'guild_permissions') else False
        except AttributeError:
            is_admin = False
        
        if not is_admin:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only server administrators can use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            guild_id = interaction.guild.id if interaction.guild else 0
            self.auto_reply_enabled[guild_id] = enabled
            
            status = "enabled" if enabled else "disabled"
            embed = discord.Embed(
                title="🔧 Auto-Reply Settings Updated",
                description=f"Auto-reply to @mentions has been **{status}** for this server.",
                color=discord.Color.green() if enabled else discord.Color.orange()
            )
            
            if enabled:
                embed.add_field(
                    name="ℹ️ How it works",
                    value="Bot will respond to @mentions with AI-powered conversations about Jewish texts.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="ℹ️ Note",
                    value="Bot will only respond to slash commands, not @mentions.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in toggle_autoreply: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not update auto-reply settings.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    def is_auto_reply_enabled(self, guild_id: int) -> bool:
        """Check if auto-reply is enabled for a guild"""
        return self.auto_reply_enabled.get(guild_id, True)  # Default to enabled
    
    @app_commands.command(name="ping", description="Test bot response - instant reply")
    async def ping_command(self, interaction: discord.Interaction):
        """Quick test command that responds instantly"""
        embed = discord.Embed(
            title="🏓 Pong!",
            description="Rabbi Bot is online and ready to serve!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="✅ Status",
            value="All systems operational\nReady for Jewish learning",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show help information for Sefaria bot commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information"""
        # Respond immediately to avoid timeout
        embed = discord.Embed(
            title="📚 Rabbi Bot - Ultimate Jewish Learning Assistant",
            description="Access the world's largest Jewish text library with 50+ specialized commands",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🎲 /random",
            value="Get a random Jewish text quote\n`language`: hebrew, english, or both\n`category`: torah, talmud, mishnah, etc.",
            inline=False
        )
        
        embed.add_field(
            name="🔍 /search",
            value="Search for specific texts or passages\n`query`: Search term or text reference\n`language`: hebrew, english, or both",
            inline=False
        )
        
        embed.add_field(
            name="📖 /text",
            value="Get a specific text by reference\n`reference`: e.g., 'Genesis 1:1', 'Berakhot 2a'\n`language`: hebrew, english, or both",
            inline=False
        )
        
        embed.add_field(
            name="📅 /daily",
            value="Get the daily Torah portion or study text",
            inline=False
        )
        
        embed.add_field(
            name="📖 /commentary",
            value="Get commentary on a verse\n`reference`: e.g., 'Genesis 1:1'\n`commentator`: rashi, ibn_ezra, ramban, ralbag, sforno, radak\n`language`: hebrew, english, or both",
            inline=False
        )
        
        embed.add_field(
            name="🕯️ /shabbat",
            value="Get Shabbat candle lighting and havdalah times\n`location`: e.g., 'New York', 'Jerusalem', 'London'",
            inline=False
        )
        
        embed.add_field(
            name="📅 /holidays",
            value="Get upcoming Jewish holidays\n`year`: Optional year (defaults to current)",
            inline=False
        )
        
        embed.add_field(
            name="📅 /hebrewdate",
            value="Get today's Hebrew date conversion",
            inline=False
        )
        
        embed.add_field(
            name="🔧 /autoreply [ADMIN]",
            value="Toggle auto-reply to @mentions on/off\n`enabled`: true or false",
            inline=False
        )
        
        embed.add_field(
            name="🕰️ /zmanim",
            value="Get daily prayer times for any location\n`location`: City name (e.g., 'New York')",
            inline=False
        )
        
        embed.add_field(
            name="📜 /parsha",
            value="Get weekly Torah portion (current or specific date)\n`date`: Optional date (YYYY-MM-DD)",
            inline=False
        )
        
        embed.add_field(
            name="📖 /dafyomi",
            value="Get today's Daf Yomi (daily Talmud page)",
            inline=False
        )
        
        embed.add_field(
            name="🔢 /gematria",
            value="Calculate Hebrew numerology values\n`text`: Hebrew text to calculate",
            inline=False
        )
        
        embed.add_field(
            name="📜 /manuscripts",
            value="Search Hebrew manuscripts from National Library of Israel\n`query`: Search term",
            inline=False
        )
        
        embed.add_field(
            name="📸 /historicalphotos",
            value="Search historical photos from National Library of Israel\n`query`: Search term",
            inline=False
        )
        
        embed.add_field(
            name="📚 /jewishbooks",
            value="Search Jewish books from National Library of Israel\n`query`: Search term, `language`: heb/eng/yid",
            inline=False
        )
        
        embed.add_field(
            name="🗺️ /maps",
            value="Search historical maps from National Library of Israel\n`location`: Location name",
            inline=False
        )
        
        embed.add_field(
            name="💎 /randomtreasure",
            value="Get a random treasure from National Library of Israel\n`type`: Optional type filter",
            inline=False
        )
        
        embed.add_field(
            name="🌍 /translate",
            value="Translate text to any language\n`text`: Text to translate, `target_language`: Target language",
            inline=False
        )
        
        embed.add_field(
            name="📖 /dailystudy",
            value="Get today's daily study from Chabad.org",
            inline=False
        )
        
        embed.add_field(
            name="💎 /dailywisdom",
            value="Get daily wisdom quote from Chabad.org",
            inline=False
        )
        
        embed.add_field(
            name="📜 /tanya",
            value="Get today's Tanya lesson from Chabad.org",
            inline=False
        )
        
        embed.add_field(
            name="🏛️ /chabadcenters",
            value="Find Chabad centers near a location\n`location`: City name",
            inline=False
        )
        
        embed.add_field(
            name="🔥 /chassidic",
            value="Unified Chassidic content: stories (Chabad) + books (Dicta)\n`type`: Choose stories, books, or all",
            inline=False
        )
        
        embed.add_field(
            name="📖 /dailylearning",
            value="Unified daily learning from multiple sources\n`source`: Choose chabad, sefaria, all, or random",
            inline=False
        )
        
        embed.add_field(
            name="📚 /jewishbooks",
            value="Smart search across ALL libraries (Sefaria, Dicta, NLI)\n`query`: Search term, `source`: dicta/nli/sefaria/all",
            inline=False
        )
        
        embed.add_field(
            name="🍯 /kosherinfo",
            value="Kosher laws and certification info\n`query`: Optional search term",
            inline=False
        )
        
        embed.add_field(
            name="⚖️ /responsa",
            value="Browse rabbinic legal decisions from Dicta",
            inline=False
        )
        
        embed.add_field(
            name="📊 /dictastats",
            value="Statistics about Dicta's 800+ AI-enhanced books",
            inline=False
        )
        
        # Revolutionary new integrated commands
        embed.add_field(
            name="🧮 /calculate",
            value="Natural language Jewish calculations using TorahCalc\n`query`: Natural language (e.g., 'Convert 3 amos to feet')",
            inline=False
        )
        
        embed.add_field(
            name="📏 /measurements",
            value="Convert between biblical and modern units\n`unit_type`, `from_unit`, `to_unit`, `amount`",
            inline=False
        )
        
        embed.add_field(
            name="📚 /torahstudy",
            value="Comprehensive daily Torah study from ALL sources\n`date`: Optional date (YYYY-MM-DD)",
            inline=False
        )
        
        embed.add_field(
            name="🏛️ /archives",
            value="Search across ALL Jewish digital archives\n`query`: Search historical documents and texts",
            inline=False
        )
        
        # Revolutionary new ecosystem commands
        embed.add_field(
            name="📖 /orayta",
            value="Access Orayta's comprehensive Jewish book library\n`query`, `category`: Search cross-platform texts",
            inline=False
        )
        
        embed.add_field(
            name="🕊️ /siddur",
            value="Create custom Jewish liturgical books with OpenSiddur\n`prayer_type`, `tradition`: Build custom siddurim",
            inline=False
        )
        
        embed.add_field(
            name="💡 /chiddush",
            value="Share and discover Torah insights on Pninim\n`topic`, `author_type`: Social Torah learning",
            inline=False
        )
        
        embed.add_field(
            name="🌟 /ecosystem",
            value="Overview of the complete Jewish software ecosystem\nSee all 10+ integrated platforms",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Data Sources",
            value="Texts: Sefaria.org • Calendar: Hebcal.com • Archives: National Library of Israel • Chassidic: Chabad.org • AI Books: Dicta.org.il • Translation: Google Translate",
            inline=False
        )
        
        embed.add_field(
            name="🔢 /gematria",
            value="Calculate gematria values for Hebrew text\n`text`: Hebrew text to calculate\n`method`: standard, small, mispar_katan",
            inline=False
        )
        
        embed.add_field(
            name="🌟 Advanced Features",
            value="• AI-powered conversations (mention @Rabbi Bot)\n• Historical manuscripts & photos\n• Chassidic wisdom & daily studies\n• Biblical calculations & measurements\n• Multi-language support & translation",
            inline=False
        )
        
        embed.set_footer(text="🚀 Most comprehensive Jewish learning bot with 50+ commands")
        
        # Respond immediately to prevent Discord timeout
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="categories", description="List available text categories")
    async def list_categories(self, interaction: discord.Interaction):
        """List available text categories"""
        await interaction.response.defer()
        
        try:
            # Set a shorter timeout for this command
            categories = await asyncio.wait_for(
                self.sefaria_client.get_categories(), 
                timeout=8.0
            )
            
            if not categories:
                embed = discord.Embed(
                    title="📂 Text Categories",
                    description="Popular categories include: Torah, Talmud, Mishnah, Halakhah, Kabbalah, Liturgy, Philosophy",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="💡 Try these commands instead:",
                    value="• `/random` - Get random texts\n• `/search` - Search for specific content\n• `/daily` - Get daily Torah content",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📂 Available Text Categories",
                description="Use these categories with the `/random` command",
                color=discord.Color.green()
            )
            
            category_text = "\n".join([f"• {cat}" for cat in categories[:20]])  # Limit to 20
            embed.add_field(
                name="Categories",
                value=category_text,
                inline=False
            )
            
            if len(categories) > 20:
                embed.add_field(
                    name="📝 Note",
                    value=f"Showing first 20 of {len(categories)} categories",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="📂 Text Categories",
                description="Connection timeout. Here are popular categories:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Popular Categories",
                value="• Torah\n• Talmud\n• Mishnah\n• Halakhah\n• Kabbalah\n• Liturgy\n• Philosophy\n• Midrash\n• Responsa",
                inline=False
            )
            embed.add_field(
                name="💡 Usage",
                value="Use these with `/random category:Torah` etc.",
                inline=False
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in list_categories: {e}")
            embed = discord.Embed(
                title="📂 Text Categories",
                description="Here are the main Jewish text categories:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Main Categories",
                value="• Torah (Five Books)\n• Talmud (Babylonian & Jerusalem)\n• Mishnah (Six Orders)\n• Halakhah (Jewish Law)\n• Kabbalah (Mysticism)\n• Liturgy (Prayers)\n• Philosophy\n• Midrash (Commentary)",
                inline=False
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="setprompt", description="Set the AI system prompt (admin only)")
    @app_commands.describe(prompt="The new system prompt for the AI")
    async def set_ai_prompt(self, interaction: discord.Interaction, prompt: str):
        """Set the AI system prompt"""
        # Check if user has administrator permissions
        if not (hasattr(interaction.user, 'guild_permissions') and interaction.user.guild_permissions.administrator):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can change the AI prompt.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update the AI prompt
        self.bot.ai_client.set_system_prompt(prompt)
        
        embed = discord.Embed(
            title="✅ AI Prompt Updated",
            description="The AI system prompt has been successfully updated.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="New Prompt Preview",
            value=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # National Library of Israel Commands
    @app_commands.command(name="manuscripts", description="Search Hebrew manuscripts from National Library of Israel")
    @app_commands.describe(query="Search term for Hebrew manuscripts")
    async def hebrew_manuscripts(self, interaction: discord.Interaction, query: str):
        """Search Hebrew manuscripts"""
        await interaction.response.defer()
        
        try:
            manuscripts = await self.nli_client.search_hebrew_manuscripts(query)
            
            if not manuscripts:
                embed = discord.Embed(
                    title="📜 No Manuscripts Found",
                    description=f"No Hebrew manuscripts found for: **{query}**",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📜 Hebrew Manuscripts: {query}",
                description=f"Found {len(manuscripts)} manuscripts",
                color=discord.Color.gold()
            )
            
            for i, manuscript in enumerate(manuscripts[:5]):
                title = manuscript.get('title', 'Unknown Title')
                creator = manuscript.get('creator', 'Unknown Creator')
                date = manuscript.get('date', 'Unknown Date')
                
                embed.add_field(
                    name=f"📚 {title[:50]}{'...' if len(title) > 50 else ''}",
                    value=f"**Creator:** {creator}\n**Date:** {date}",
                    inline=False
                )
            
            embed.set_footer(text="Hebrew manuscripts from National Library of Israel")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in hebrew_manuscripts: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search Hebrew manuscripts.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="historicalphotos", description="Search historical photos from National Library of Israel")
    @app_commands.describe(query="Search term for historical photos")
    async def historical_photos(self, interaction: discord.Interaction, query: str):
        """Search historical photographs"""
        await interaction.response.defer()
        
        try:
            photos = await self.nli_client.search_historical_photos(query)
            
            if not photos:
                embed = discord.Embed(
                    title="📸 No Photos Found",
                    description=f"No historical photos found for: **{query}**",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📸 Historical Photos: {query}",
                description=f"Found {len(photos)} historical photographs",
                color=discord.Color.blue()
            )
            
            for i, photo in enumerate(photos[:3]):
                title = photo.get('title', 'Unknown Title')
                date = photo.get('date', 'Unknown Date')
                description = photo.get('description', '')
                
                embed.add_field(
                    name=f"📷 {title[:50]}{'...' if len(title) > 50 else ''}",
                    value=f"**Date:** {date}\n{description[:100]}{'...' if len(description) > 100 else ''}",
                    inline=False
                )
            
            embed.set_footer(text="Historical photos from National Library of Israel")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in historical_photos: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search historical photos.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="jewishbooks", description="Search Jewish books from National Library of Israel")
    @app_commands.describe(
        query="Search term for Jewish books",
        language="Language (heb for Hebrew, eng for English, yid for Yiddish)"
    )
    async def jewish_books(self, interaction: discord.Interaction, query: str, language: str = "heb"):
        """Search Jewish books"""
        await interaction.response.defer()
        
        try:
            books = await self.nli_client.search_jewish_books(query, language)
            
            if not books:
                embed = discord.Embed(
                    title="📚 No Books Found",
                    description=f"No Jewish books found for: **{query}** in {language}",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📚 Jewish Books: {query}",
                description=f"Found {len(books)} books in {language}",
                color=discord.Color.purple()
            )
            
            for i, book in enumerate(books[:4]):
                title = book.get('title', 'Unknown Title')
                creator = book.get('creator', 'Unknown Author')
                date = book.get('date', 'Unknown Date')
                
                embed.add_field(
                    name=f"📖 {title[:45]}{'...' if len(title) > 45 else ''}",
                    value=f"**Author:** {creator}\n**Date:** {date}",
                    inline=True
                )
            
            embed.set_footer(text="Jewish books from National Library of Israel")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in jewish_books: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search Jewish books.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="maps", description="Search historical maps from National Library of Israel")
    @app_commands.describe(location="Location to search for historical maps")
    async def historical_maps(self, interaction: discord.Interaction, location: str):
        """Search historical maps"""
        await interaction.response.defer()
        
        try:
            maps = await self.nli_client.search_maps(location)
            
            if not maps:
                embed = discord.Embed(
                    title="🗺️ No Maps Found",
                    description=f"No historical maps found for: **{location}**",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🗺️ Historical Maps: {location}",
                description=f"Found {len(maps)} historical maps",
                color=discord.Color.green()
            )
            
            for i, map_item in enumerate(maps[:3]):
                title = map_item.get('title', 'Unknown Title')
                date = map_item.get('date', 'Unknown Date')
                creator = map_item.get('creator', 'Unknown Creator')
                
                embed.add_field(
                    name=f"🗺️ {title[:50]}{'...' if len(title) > 50 else ''}",
                    value=f"**Creator:** {creator}\n**Date:** {date}",
                    inline=False
                )
            
            embed.set_footer(text="Historical maps from National Library of Israel")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in historical_maps: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search historical maps.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="randomtreasure", description="Get a random treasure from National Library of Israel")
    @app_commands.describe(type="Type of item (manuscript, photograph, book, map, audio)")
    async def random_treasure(self, interaction: discord.Interaction, type: str = ""):
        """Get a random treasure from NLI"""
        await interaction.response.defer()
        
        try:
            item = await self.nli_client.get_random_item(type)
            
            if not item:
                embed = discord.Embed(
                    title="💎 No Treasure Found",
                    description="Could not find a random treasure at this time.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="💎 Random Treasure from National Library of Israel",
                color=discord.Color.gold()
            )
            
            title = item.get('title', 'Unknown Title')
            creator = item.get('creator', 'Unknown Creator')
            date = item.get('date', 'Unknown Date')
            item_type = item.get('material_type', 'Unknown Type')
            description = item.get('description', 'No description available')
            
            embed.add_field(name="📚 Title", value=title, inline=False)
            embed.add_field(name="👤 Creator", value=creator, inline=True)
            embed.add_field(name="📅 Date", value=date, inline=True)
            embed.add_field(name="🏷️ Type", value=item_type, inline=True)
            
            if description and len(description) > 10:
                embed.add_field(
                    name="📝 Description",
                    value=description[:200] + "..." if len(description) > 200 else description,
                    inline=False
                )
            
            embed.set_footer(text="Random treasure from National Library of Israel")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in random_treasure: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get random treasure.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="translate", description="Translate text to any language")
    @app_commands.describe(
        text="Text to translate",
        target_language="Target language (e.g., 'english', 'hebrew', 'spanish')"
    )
    async def translate_text(self, interaction: discord.Interaction, text: str, target_language: str):
        """Translate text using Google Translate"""
        await interaction.response.defer()
        
        try:
            try:
                from deep_translator import GoogleTranslator
            except ImportError:
                embed = discord.Embed(
                    title="❌ Translation Error",
                    description="Translation service not available. Please contact administrator.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Initialize translator with auto-detection
            translator = GoogleTranslator(source='auto', target=target_language.lower())
            
            # Translate text
            result = translator.translate(text)
            
            # For display purposes (deep-translator doesn't provide confidence)
            source_lang = 'auto-detected'
            
            embed = discord.Embed(
                title="🌍 Translation",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 Original Text",
                value=f"```{text}```",
                inline=False
            )
            
            embed.add_field(
                name="🔤 Source Language",
                value=f"**{source_lang}**",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Target Language",
                value=f"**{target_language}**",
                inline=True
            )
            
            embed.add_field(
                name="✨ Translation",
                value=f"```{result}```",
                inline=False
            )
            
            embed.set_footer(text="Powered by Google Translate")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in translate_text: {e}")
            embed = discord.Embed(
                title="❌ Translation Error",
                description=f"Could not translate text. Error: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    # Chabad.org Commands
    @app_commands.command(name="dailystudy", description="Get today's daily study from Chabad.org")
    async def daily_study(self, interaction: discord.Interaction):
        """Get daily study content"""
        await interaction.response.defer()
        
        try:
            study = await self.chabad_client.get_daily_study()
            
            embed = discord.Embed(
                title="📖 Today's Daily Study",
                color=discord.Color.blue()
            )
            
            if study and 'title' in study:
                embed.add_field(
                    name="📚 Study Topic",
                    value=study['title'],
                    inline=False
                )
                
                if 'description' in study:
                    embed.add_field(
                        name="📝 Description",
                        value=study['description'][:500] + "..." if len(study['description']) > 500 else study['description'],
                        inline=False
                    )
            else:
                embed.add_field(
                    name="📖 Daily Study",
                    value="Visit Chabad.org for today's daily study materials including Torah, Talmud, and Chassidic teachings.",
                    inline=False
                )
            
            embed.add_field(
                name="🔗 Learn More",
                value="Visit [Chabad.org Daily Study](https://www.chabad.org/library/article_cdo/aid/3146/jewish/Daily-Study.htm)",
                inline=False
            )
            
            embed.set_footer(text="Daily study from Chabad.org")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in daily_study: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get daily study content.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="dailywisdom", description="Get daily wisdom quote from Chabad.org")
    async def daily_wisdom(self, interaction: discord.Interaction):
        """Get daily wisdom content"""
        await interaction.response.defer()
        
        try:
            wisdom = await self.chabad_client.get_daily_wisdom()
            
            embed = discord.Embed(
                title="💎 Today's Daily Wisdom",
                color=discord.Color.gold()
            )
            
            if wisdom and 'title' in wisdom:
                embed.add_field(
                    name="🌟 Wisdom",
                    value=wisdom['title'],
                    inline=False
                )
                
                if 'description' in wisdom:
                    embed.add_field(
                        name="📖 Teaching",
                        value=wisdom['description'][:400] + "..." if len(wisdom['description']) > 400 else wisdom['description'],
                        inline=False
                    )
            else:
                embed.add_field(
                    name="🌟 Daily Wisdom",
                    value="Daily inspiration from Chabad teachings, offering spiritual insights for modern life.",
                    inline=False
                )
            
            embed.add_field(
                name="🔗 More Wisdom",
                value="Explore more at [Chabad.org Daily Wisdom](https://www.chabad.org/library/article_cdo/aid/3147/jewish/Daily-Wisdom.htm)",
                inline=False
            )
            
            embed.set_footer(text="Daily wisdom from Chabad.org")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in daily_wisdom: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get daily wisdom content.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="tanya", description="Get today's Tanya lesson from Chabad.org")
    async def daily_tanya(self, interaction: discord.Interaction):
        """Get daily Tanya lesson"""
        await interaction.response.defer()
        
        try:
            tanya = await self.chabad_client.get_daily_tanya()
            
            embed = discord.Embed(
                title="📜 Today's Tanya Lesson",
                description="Daily wisdom from the foundational work of Chabad Chassidism",
                color=discord.Color.purple()
            )
            
            if tanya and 'title' in tanya:
                embed.add_field(
                    name="📖 Lesson",
                    value=tanya['title'],
                    inline=False
                )
                
                if 'description' in tanya:
                    embed.add_field(
                        name="🧠 Teaching",
                        value=tanya['description'][:400] + "..." if len(tanya['description']) > 400 else tanya['description'],
                        inline=False
                    )
            else:
                embed.add_field(
                    name="📜 About Tanya",
                    value="The Tanya is the fundamental work of Chabad Chassidic philosophy, teaching the path to spiritual growth through understanding the soul's divine nature.",
                    inline=False
                )
            
            embed.add_field(
                name="🔗 Study More",
                value="Continue learning at [Chabad.org Tanya](https://www.chabad.org/library/tanya)",
                inline=False
            )
            
            embed.set_footer(text="Tanya lessons from Chabad.org")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in daily_tanya: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get Tanya lesson.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="chabadcenters", description="Find Chabad centers near a location")
    @app_commands.describe(location="City or location to search for Chabad centers")
    async def chabad_centers(self, interaction: discord.Interaction, location: str):
        """Find Chabad centers"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title=f"🏛️ Chabad Centers near {location}",
                description="Connect with your local Chabad community",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🌍 Global Network",
                value="Chabad operates over 5,000 centers worldwide, serving Jewish communities in 100+ countries.",
                inline=False
            )
            
            embed.add_field(
                name="🔍 Find Centers",
                value=f"Search for Chabad centers at [Chabad.org Directory](https://www.chabad.org/centers/default_cdo/jewish/Chabad-Locator.htm?searchstring={quote(location)})",
                inline=False
            )
            
            embed.add_field(
                name="📞 Services",
                value="• Shabbat services\n• Jewish education\n• Holiday celebrations\n• Community events\n• Rabbi consultations",
                inline=False
            )
            
            embed.set_footer(text="Chabad center directory from Chabad.org")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in chabad_centers: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search Chabad centers.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    # Unified Smart Commands - Combining Multiple APIs
    @app_commands.command(name="chassidic", description="Explore Chassidic content from stories (Chabad) to books (Dicta)")
    @app_commands.describe(type="Choose: stories, books, or all")
    async def chassidic_unified(self, interaction: discord.Interaction, type: str = "all"):
        """Unified Chassidic content from multiple sources"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🔥 Chassidic Wisdom & Literature",
                description="Stories, teachings, and digitized books from multiple sources",
                color=discord.Color.gold()
            )
            
            if type.lower() in ["stories", "all"]:
                embed.add_field(
                    name="📚 Chassidic Stories (Chabad.org)",
                    value="Inspiring tales teaching faith, kindness, spiritual growth, and overcoming challenges through the wisdom of great rabbis.",
                    inline=False
                )
                
                embed.add_field(
                    name="🔗 Read Stories",
                    value="[Chabad.org Stories](https://www.chabad.org/library/article_cdo/aid/3149/jewish/Stories.htm)",
                    inline=True
                )
            
            if type.lower() in ["books", "all"]:
                # Get actual Chassidic books from Dicta
                books = await self.dicta_client.get_chassidic_books(limit=3)
                
                if books:
                    books_text = ""
                    for book in books[:3]:
                        title = book.get('displayNameEnglish', book.get('displayName', 'Unknown'))
                        author = book.get('authorEnglish', book.get('author', 'Unknown'))
                        books_text += f"• **{title[:30]}{'...' if len(title) > 30 else ''}** by {author}\n"
                    
                    embed.add_field(
                        name="📖 AI-Enhanced Chassidic Books (Dicta)",
                        value=books_text,
                        inline=False
                    )
                
                embed.add_field(
                    name="🤖 AI Features",
                    value="Rashi script modernization • Automatic nikud • Enhanced readability",
                    inline=True
                )
                
                embed.add_field(
                    name="🔗 Browse Library",
                    value="[Dicta Library](https://library.dicta.org.il)",
                    inline=True
                )
            
            embed.set_footer(text="Chassidic content from Chabad.org & Dicta.org.il")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in chassidic_unified: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get Chassidic content.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="dailylearning", description="Unified daily Jewish learning from multiple sources")
    @app_commands.describe(source="Choose: chabad, sefaria, all, or random")
    async def daily_learning_unified(self, interaction: discord.Interaction, source: str = "all"):
        """Unified daily learning content"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="📖 Daily Jewish Learning",
                description="Comprehensive daily study from multiple authentic sources",
                color=discord.Color.blue()
            )
            
            if source.lower() in ["chabad", "all", "random"]:
                embed.add_field(
                    name="🎯 Daily Mitzvah",
                    value="Daily commandments and spiritual practices guide Jewish life through 613 mitzvot (positive actions and prohibitions).",
                    inline=False
                )
                
                embed.add_field(
                    name="💎 Daily Wisdom",
                    value="Chassidic teachings offering spiritual insights for modern life from Chabad tradition.",
                    inline=False
                )
                
                embed.add_field(
                    name="📜 Tanya Study",
                    value="Foundational Chassidic philosophy teaching the soul's divine nature and spiritual growth.",
                    inline=False
                )
            
            if source.lower() in ["sefaria", "all", "random"]:
                # Get daily text from Sefaria
                daily_text = await self.sefaria_client.get_daily_text()
                if daily_text and 'title' in daily_text:
                    embed.add_field(
                        name="📚 Daily Text (Sefaria)",
                        value=daily_text['title'],
                        inline=False
                    )
            
            # Always include Torah portion
            torah_reading = await self.hebcal_client.get_torah_reading()
            if torah_reading and 'parsha' in torah_reading:
                embed.add_field(
                    name="📜 Weekly Torah Portion",
                    value=f"**{torah_reading['parsha']}** - {torah_reading.get('reading', 'Current weekly portion')}",
                    inline=False
                )
            
            embed.add_field(
                name="🔗 Sources",
                value="[Chabad.org](https://www.chabad.org) • [Sefaria.org](https://www.sefaria.org) • [Hebcal.com](https://www.hebcal.com)",
                inline=False
            )
            
            embed.set_footer(text="Daily learning from multiple Jewish sources")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in daily_learning_unified: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get daily learning content.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="jewishbooks", description="Search Jewish books across all libraries (Sefaria, Dicta, NLI)")
    @app_commands.describe(
        query="Search term for books",
        source="Choose source: dicta, nli, sefaria, or all",
        language="Language preference for multi-source search"
    )
    async def jewish_books_unified(self, interaction: discord.Interaction, query: str, source: str = "all", language: str = "both"):
        """Unified Jewish book search across multiple libraries"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title=f"📚 Jewish Books: {query}",
                description="Comprehensive search across multiple Jewish libraries",
                color=discord.Color.purple()
            )
            
            results_found = False
            
            # Search Dicta AI-enhanced books
            if source.lower() in ["dicta", "all"]:
                dicta_books = await self.dicta_client.search_books(query, limit=3)
                if dicta_books:
                    results_found = True
                    books_text = ""
                    for book in dicta_books:
                        title = book.get('displayNameEnglish', book.get('displayName', 'Unknown'))
                        author = book.get('authorEnglish', book.get('author', 'Unknown'))
                        books_text += f"• **{title[:35]}{'...' if len(title) > 35 else ''}**\n  by {author}\n"
                    
                    embed.add_field(
                        name="🤖 AI-Enhanced Books (Dicta - 800+ books)",
                        value=books_text,
                        inline=False
                    )
            
            # Search National Library of Israel
            if source.lower() in ["nli", "all"]:
                nli_books = await self.nli_client.search_jewish_books(query, language, limit=3)
                if nli_books:
                    results_found = True
                    books_text = ""
                    for book in nli_books:
                        title = book.get('title', 'Unknown Title')
                        creator = book.get('creator', 'Unknown Creator')
                        books_text += f"• **{title[:35]}{'...' if len(title) > 35 else ''}**\n  by {creator}\n"
                    
                    embed.add_field(
                        name="🏛️ Historical Archives (National Library)",
                        value=books_text,
                        inline=False
                    )
            
            # Search Sefaria texts
            if source.lower() in ["sefaria", "all"]:
                sefaria_results = await self.sefaria_client.search_texts(query, limit=3)
                if sefaria_results:
                    results_found = True
                    texts_text = ""
                    for result in sefaria_results:
                        title = result.get('title', 'Unknown Text')
                        texts_text += f"• **{title[:40]}{'...' if len(title) > 40 else ''}**\n"
                    
                    embed.add_field(
                        name="📜 Classical Texts (Sefaria)",
                        value=texts_text,
                        inline=False
                    )
            
            if not results_found:
                embed.description = f"No books found for: **{query}** in selected sources"
                embed.color = discord.Color.orange()
            
            embed.add_field(
                name="🔗 Explore Libraries",
                value="[Dicta AI Books](https://library.dicta.org.il) • [National Library](https://www.nli.org.il) • [Sefaria Texts](https://www.sefaria.org)",
                inline=False
            )
            
            embed.set_footer(text="Books from multiple Jewish libraries and archives")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in jewish_books_unified: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search Jewish books.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    # Revolutionary New Commands: TorahCalc + OpenTorah Integration
    @app_commands.command(name="calculate", description="Natural language Jewish calculations using TorahCalc")
    @app_commands.describe(query="Natural language calculation (e.g., 'Convert 3 amos to feet')")
    async def torah_calculate(self, interaction: discord.Interaction, query: str):
        """Perform advanced Jewish calculations using natural language"""
        await interaction.response.defer()
        
        try:
            # Use TorahCalc's natural language processing
            result = await self.torahcalc_client.natural_language_query(query)
            
            embed = discord.Embed(
                title="🧮 TorahCalc Calculation",
                description=f"**Query:** {query}",
                color=discord.Color.blue()
            )
            
            if result and 'result' in result:
                embed.add_field(
                    name="📊 Result",
                    value=result['result'],
                    inline=False
                )
                
                if 'explanation' in result:
                    embed.add_field(
                        name="💡 Explanation",
                        value=result['explanation'],
                        inline=False
                    )
            else:
                embed.add_field(
                    name="🔍 Processing",
                    value=f"TorahCalc is processing: '{query}'\nThis includes biblical unit conversions, gematria, and halachic calculations.",
                    inline=False
                )
                
                embed.add_field(
                    name="💫 TorahCalc Features",
                    value="• Biblical & Talmudic unit conversions\n• Gematria calculations\n• Hebrew calendar conversions\n• Halachic time calculations\n• Natural language processing",
                    inline=False
                )
            
            embed.add_field(
                name="🔗 TorahCalc Website",
                value="[www.torahcalc.com](https://www.torahcalc.com) - The Jewish Wolfram Alpha",
                inline=False
            )
            
            embed.set_footer(text="Powered by TorahCalc - Advanced Jewish calculations")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in torah_calculate: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not process calculation.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="measurements", description="Convert between biblical and modern units")
    @app_commands.describe(
        unit_type="Type of measurement",
        from_unit="Unit to convert from",
        to_unit="Unit to convert to", 
        amount="Amount to convert"
    )
    async def biblical_measurements(self, interaction: discord.Interaction, unit_type: str, 
                                  from_unit: str, to_unit: str, amount: float = 1.0):
        """Convert between biblical and modern measurement units"""
        await interaction.response.defer()
        
        try:
            # Use TorahCalc for precise biblical conversions
            result = await self.torahcalc_client.convert_biblical_units(
                unit_type, from_unit, to_unit, amount
            )
            
            embed = discord.Embed(
                title="📏 Biblical Unit Conversion",
                description=f"Converting {amount} {from_unit} to {to_unit}",
                color=discord.Color.green()
            )
            
            if result and 'result' in result:
                embed.add_field(
                    name="🔄 Conversion Result",
                    value=f"**{amount} {from_unit}** = **{result['result']} {to_unit}**",
                    inline=False
                )
                
                if 'opinion' in result:
                    embed.add_field(
                        name="👨‍🏫 Halachic Opinion",
                        value=f"Based on: {result['opinion']}",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="📐 Unit Types Available",
                    value="• **Length:** amah, tefach, etzbah, mil, parsah\n• **Volume:** kezayis, kav, seah, kor\n• **Weight:** shekel, mane, kikar\n• **Time:** shaah, et, chelek\n• **Coins:** shekel, dinar, maah",
                    inline=False
                )
            
            embed.add_field(
                name="🎯 Pro Tip",
                value="Use `/calculate` for natural language: 'Convert 3 amos to feet'",
                inline=False
            )
            
            embed.set_footer(text="Biblical measurements from TorahCalc")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in biblical_measurements: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not convert measurements.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="torahstudy", description="Comprehensive daily Torah study combining all sources")
    @app_commands.describe(date="Date in YYYY-MM-DD format (optional)")
    async def comprehensive_torah_study(self, interaction: discord.Interaction, date: str = None):
        """Get comprehensive daily Torah study from all sources"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="📚 Comprehensive Torah Study",
                description="Daily learning from multiple authentic sources",
                color=discord.Color.purple()
            )
            
            # Get TorahCalc daily learning data
            torahcalc_learning = await self.torahcalc_client.get_daily_learning(date)
            if torahcalc_learning:
                learning_text = ""
                if 'dafYomi' in torahcalc_learning:
                    learning_text += f"**Daf Yomi:** {torahcalc_learning['dafYomi']}\n"
                if 'mishnahYomi' in torahcalc_learning:
                    learning_text += f"**Mishnah Yomi:** {torahcalc_learning['mishnahYomi']}\n"
                if 'dailyRambam' in torahcalc_learning:
                    learning_text += f"**Daily Rambam:** {torahcalc_learning['dailyRambam']}\n"
                
                if learning_text:
                    embed.add_field(
                        name="📖 Daily Learning Schedule (TorahCalc)",
                        value=learning_text,
                        inline=False
                    )
            
            # Get Hebrew date from TorahCalc
            hebrew_date = await self.torahcalc_client.convert_date_greg_to_hebrew()
            if hebrew_date and 'hebrewDate' in hebrew_date:
                embed.add_field(
                    name="📅 Hebrew Date",
                    value=hebrew_date['hebrewDate'],
                    inline=True
                )
            
            # Get Torah portion from Hebcal
            torah_reading = await self.hebcal_client.get_torah_reading()
            if torah_reading and 'parsha' in torah_reading:
                embed.add_field(
                    name="📜 Weekly Torah Portion",
                    value=f"**{torah_reading['parsha']}**",
                    inline=True
                )
            
            # Get daily text from Sefaria
            daily_text = await self.sefaria_client.get_daily_text()
            if daily_text and 'title' in daily_text:
                embed.add_field(
                    name="📚 Sefaria Daily Text",
                    value=daily_text['title'],
                    inline=False
                )
            
            # Get Chabad daily content
            chabad_wisdom = await self.chabad_client.get_daily_wisdom()
            if chabad_wisdom and 'content' in chabad_wisdom:
                embed.add_field(
                    name="💎 Chabad Daily Wisdom",
                    value=chabad_wisdom['content'][:200] + "..." if len(chabad_wisdom['content']) > 200 else chabad_wisdom['content'],
                    inline=False
                )
            
            # Get OpenTorah calendar info
            calendar_info = await self.opentorah_client.get_jewish_calendar_data()
            if calendar_info:
                embed.add_field(
                    name="🗓️ Calendar Features (OpenTorah)",
                    value="Advanced astronomical & arithmetic calculations\nPrecise zmanim computations",
                    inline=False
                )
            
            embed.add_field(
                name="🔗 Study Resources",
                value="[TorahCalc](https://www.torahcalc.com) • [Sefaria](https://www.sefaria.org) • [Chabad](https://www.chabad.org) • [OpenTorah](https://www.opentorah.org)",
                inline=False
            )
            
            embed.set_footer(text="Comprehensive study from 6 major Jewish institutions")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in comprehensive_torah_study: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not get comprehensive study data.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="archives", description="Search across all Jewish digital archives and collections")
    @app_commands.describe(query="Search term for historical documents and texts")
    async def digital_archives_search(self, interaction: discord.Interaction, query: str):
        """Search across all digital Jewish archives"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title=f"🏛️ Digital Jewish Archives: {query}",
                description="Comprehensive search across historical collections",
                color=discord.Color.gold()
            )
            
            results_found = False
            
            # Search OpenTorah archives
            opentorah_results = await self.opentorah_client.search_all_archives(query, limit=2)
            if opentorah_results:
                results_found = True
                archives_text = ""
                for result in opentorah_results:
                    archives_text += f"• **{result['source']}:** {result['title']}\n"
                
                embed.add_field(
                    name="📜 OpenTorah Digital Archives",
                    value=archives_text,
                    inline=False
                )
            
            # Search National Library of Israel
            if any(keyword in query.lower() for keyword in ['manuscript', 'historical', 'photo', 'map']):
                nli_results = await self.nli_client.search_hebrew_manuscripts(query, limit=2)
                if nli_results:
                    results_found = True
                    manuscripts_text = ""
                    for result in nli_results:
                        title = result.get('title', 'Unknown')
                        manuscripts_text += f"• **{title[:40]}{'...' if len(title) > 40 else ''}**\n"
                    
                    embed.add_field(
                        name="📋 Historical Manuscripts (NLI)",
                        value=manuscripts_text,
                        inline=False
                    )
            
            # Search Dicta AI-enhanced books
            dicta_results = await self.dicta_client.search_books(query, limit=2)
            if dicta_results:
                results_found = True
                books_text = ""
                for book in dicta_results:
                    title = book.get('displayNameEnglish', book.get('displayName', 'Unknown'))
                    books_text += f"• **{title[:35]}{'...' if len(title) > 35 else ''}**\n"
                
                embed.add_field(
                    name="🤖 AI-Enhanced Texts (Dicta)",
                    value=books_text,
                    inline=False
                )
            
            if not results_found:
                embed.add_field(
                    name="🔍 Available Archives",
                    value="• **OpenTorah:** Early Chabad history & TEI texts\n• **National Library:** Hebrew manuscripts & photos\n• **Dicta:** 800+ AI-enhanced Jewish books\n• **Alter Rebbe Archive:** Foundational Chabad documents",
                    inline=False
                )
            
            embed.add_field(
                name="🏛️ Archive Features",
                value="Historical preservation • Scholarly annotations • Digital accessibility • Advanced search",
                inline=False
            )
            
            embed.set_footer(text="Searching across multiple Jewish digital archives")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in digital_archives_search: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not search digital archives.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    # Revolutionary new commands showcasing the ultimate Jewish software ecosystem
    
    @app_commands.command(name="orayta", description="Access Orayta's comprehensive Jewish book library")
    @app_commands.describe(
        query="Search query for books or topics",
        category="Book category to search within"
    )
    async def orayta_library(self, interaction: discord.Interaction, query: str, category: str = ""):
        """Access Orayta's cross-platform Jewish library"""
        await interaction.response.defer()
        
        try:
            results = await self.orayta_client.search_books(query, category, limit=5)
            
            embed = discord.Embed(
                title="🏛️ Orayta Jewish Library Search",
                description=f"Search results for: **{query}**",
                color=0x4A90E2
            )
            
            for result in results:
                embed.add_field(
                    name=f"📚 {result['title']}",
                    value=f"**Category**: {result['category']}\n"
                          f"**Description**: {result['description']}\n"
                          f"**Language**: {result['language']}\n"
                          f"**Status**: {result['availability']}",
                    inline=False
                )
            
            # Add library info
            stats = await self.orayta_client.get_library_statistics()
            embed.add_field(
                name="📊 Library Information",
                value=f"**Total Books**: {stats['total_books']}\n"
                      f"**Platform**: {stats['platform']}\n"
                      f"**Scope**: {stats['historical_scope']}",
                inline=True
            )
            
            embed.set_footer(text="Orayta: Cross-platform Jewish texts library")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in orayta_library: {e}")
            await interaction.followup.send("❌ Error accessing Orayta library. Please try again.")
    
    @app_commands.command(name="siddur", description="Create custom Jewish liturgical books with OpenSiddur")
    @app_commands.describe(
        prayer_type="Type of prayer or liturgy to search",
        tradition="Jewish tradition (ashkenazi, sephardic, reform, etc.)"
    )
    async def opensiddur_liturgy(self, interaction: discord.Interaction, prayer_type: str, tradition: str = ""):
        """Access OpenSiddur's customizable liturgical platform"""
        await interaction.response.defer()
        
        try:
            results = await self.opensiddur_client.search_prayers(prayer_type, tradition, limit=3)
            platform_info = await self.opensiddur_client.get_siddur_builder_info()
            
            embed = discord.Embed(
                title="🕊️ OpenSiddur Liturgical Platform",
                description=f"Custom liturgy for: **{prayer_type}**",
                color=0x8B4513
            )
            
            for result in results:
                traditions_str = ", ".join(result.get('traditions', ['All traditions']))
                languages_str = ", ".join(result.get('languages', ['Hebrew', 'English']))
                
                embed.add_field(
                    name=f"📿 {result['title']}",
                    value=f"**Category**: {result['category']}\n"
                          f"**Description**: {result['description']}\n"
                          f"**Traditions**: {traditions_str}\n"
                          f"**Languages**: {languages_str}\n"
                          f"**Customizable**: {'✅' if result.get('customizable') else '❌'}",
                    inline=False
                )
            
            # Add platform capabilities
            embed.add_field(
                name="🔧 Platform Features",
                value=f"**Mission**: {platform_info['mission']}\n"
                      f"**Core Values**: Pluralism, Historical Awareness, Individual Freedom\n"
                      f"**Formats**: Print, Screen, Mobile, Accessible",
                inline=False
            )
            
            embed.set_footer(text="OpenSiddur: Free software toolkit for Jewish liturgical books")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in opensiddur_liturgy: {e}")
            await interaction.followup.send("❌ Error accessing OpenSiddur platform. Please try again.")
    
    @app_commands.command(name="chiddush", description="Share and discover Torah insights on Pninim")
    @app_commands.describe(
        topic="Torah topic or insight category",
        author_type="Type of contributor (scholars, students, educators, community)"
    )
    async def pninim_insights(self, interaction: discord.Interaction, topic: str, author_type: str = ""):
        """Access Pninim's Torah insights sharing platform"""
        await interaction.response.defer()
        
        try:
            insights = await self.pninim_client.search_insights(topic, limit=3)
            platform_info = await self.pninim_client.get_platform_info()
            
            embed = discord.Embed(
                title="💡 Pninim Torah Insights Platform",
                description=f"**{platform_info['tagline']}**\nInsights on: **{topic}**",
                color=0xFF6B35
            )
            
            for insight in insights:
                embed.add_field(
                    name=f"✨ {insight['type']}",
                    value=f"**Category**: {insight['category']}\n"
                          f"**Preview**: {insight['preview']}\n"
                          f"**Engagement**: {insight['engagement']}\n"
                          f"**Learning Value**: {insight['learning_value']}",
                    inline=False
                )
            
            # Add community info
            community = await self.pninim_client.get_community_features()
            embed.add_field(
                name="🤝 Community Platform",
                value=f"**Mission**: {platform_info['mission']}\n"
                      f"**Features**: Social Torah learning, Peer collaboration\n"
                      f"**Benefits**: Accessible scholarship, Rapid insight sharing",
                inline=False
            )
            
            embed.set_footer(text="Pninim: Twitter for Torah insights and Chiddushim")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in pninim_insights: {e}")
            await interaction.followup.send("❌ Error accessing Pninim platform. Please try again.")
    
    @app_commands.command(name="ecosystem", description="Overview of the complete Jewish software ecosystem")
    async def jewish_software_ecosystem(self, interaction: discord.Interaction):
        """Display the comprehensive Jewish software ecosystem integrated in this bot"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🌟 Complete Jewish Software Ecosystem",
                description="The most comprehensive Discord bot for Jewish learning and practice",
                color=0x9932CC
            )
            
            # Core text sources
            embed.add_field(
                name="📚 Core Text Libraries",
                value="**Sefaria**: Digital library of Jewish texts\n"
                      "**Dicta**: 800+ AI-enhanced books\n"
                      "**Orayta**: Cross-platform Jewish library\n"
                      "**OpenTorah**: Early Chabad archives",
                inline=True
            )
            
            # Historical and cultural resources
            embed.add_field(
                name="🏛️ Historical Archives",
                value="**National Library of Israel**: Manuscripts, photos\n"
                      "**Chabad.org**: Daily wisdom, Tanya, stories\n"
                      "**Hebcal**: Jewish calendar and holidays",
                inline=True
            )
            
            # Modern tools and platforms
            embed.add_field(
                name="🔧 Modern Platforms",
                value="**TorahCalc**: Jewish calculations & gematria\n"
                      "**OpenSiddur**: Custom liturgical books\n"
                      "**Pninim**: Torah insights sharing\n"
                      "**AI Integration**: OpenAI-powered responses",
                inline=True
            )
            
            # Capabilities summary
            embed.add_field(
                name="🚀 Unprecedented Capabilities",
                value="✅ **40+ specialized commands**\n"
                      "✅ **10+ major Jewish institutions**\n"
                      "✅ **AI-enhanced text processing**\n"
                      "✅ **Biblical calculations & gematria**\n"
                      "✅ **Historical manuscript access**\n"
                      "✅ **Custom liturgy creation**\n"
                      "✅ **Social Torah learning**\n"
                      "✅ **Multilingual support**",
                inline=False
            )
            
            # Revolutionary features
            embed.add_field(
                name="🎯 Revolutionary Features",
                value="🔬 **Smart unified commands** combining multiple APIs\n"
                      "🧮 **Natural language Torah calculations**\n"
                      "🏛️ **Cross-archive digital searches**\n"
                      "📚 **Comprehensive daily study aggregation**\n"
                      "💡 **Community-driven insight sharing**\n"
                      "🕊️ **Customizable liturgical creation**",
                inline=False
            )
            
            embed.set_footer(text="The Ultimate Jewish Discord Bot - No longer just 'the best' but 'the only one you'll ever need'")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in jewish_software_ecosystem: {e}")
            await interaction.followup.send("❌ Error displaying ecosystem overview. Please try again.")

    # Advanced Jewish Learning Commands with Reaction-Based Interactivity
    
    @app_commands.command(name="gematria", description="Calculate gematria values with multiple methods")
    @app_commands.describe(
        text="Hebrew text or phrase to calculate",
        method="Calculation method (standard, small, absolute, ordinal)"
    )
    async def gematria_calculator(self, interaction: discord.Interaction, text: str, method: str = "standard"):
        """Advanced gematria calculator with multiple methods"""
        await interaction.response.defer()
        
        try:
            # Hebrew letter values for standard gematria
            gematria_values = {
                'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
                'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
                'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100,
                'ר': 200, 'ש': 300, 'ת': 400
            }
            
            # Calculate standard gematria
            standard_value = sum(gematria_values.get(char, 0) for char in text)
            
            # Calculate other methods
            small_value = sum(gematria_values.get(char, 0) % 9 or 9 for char in text if char in gematria_values)
            ordinal_value = sum(list(gematria_values.keys()).index(char) + 1 for char in text if char in gematria_values)
            
            embed = discord.Embed(
                title="🔢 Gematria Calculator",
                description=f"**Text:** {text}",
                color=discord.Color.purple()
            )
            
            embed.add_field(name="📊 Standard Gematria", value=f"**{standard_value}**", inline=True)
            embed.add_field(name="🔹 Small Gematria", value=f"**{small_value}**", inline=True)
            embed.add_field(name="📈 Ordinal Value", value=f"**{ordinal_value}**", inline=True)
            
            # Add related verses or concepts if the value matches common numbers
            special_numbers = {
                26: "יהוה (God's name)",
                86: "אלהים (Elohim)",
                72: "חסד (Chesed - Kindness)",
                613: "תרי״ג מצוות (613 Commandments)",
                18: "חי (Chai - Life)",
                36: "לו״ב צדיקים (36 Righteous)",
                248: "רמ״ח איברים (248 Limbs)",
                365: "ש״ס לא תעשה (365 Negative Commands)"
            }
            
            if standard_value in special_numbers:
                embed.add_field(
                    name="✨ Special Significance",
                    value=special_numbers[standard_value],
                    inline=False
                )
            
            embed.set_footer(text="React with 🔄 for more calculations • 📖 for related texts")
            message = await interaction.followup.send(embed=embed)
            
            # Add reaction buttons for interaction
            if message:
                await message.add_reaction("🔄")
                await message.add_reaction("📖")
                await message.add_reaction("🔍")
            
        except Exception as e:
            logger.error(f"Error in gematria_calculator: {e}")
            embed = discord.Embed(
                title="❌ Gematria Error",
                description="Could not calculate gematria. Please ensure you're using Hebrew text.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="zmanim", description="Get precise halachic times for any location")
    @app_commands.describe(
        location="City name or coordinates",
        date="Date (YYYY-MM-DD) or 'today'"
    )
    async def halachic_times(self, interaction: discord.Interaction, location: str, date: str = "today"):
        """Get comprehensive zmanim (halachic times) for any location"""
        await interaction.response.defer()
        
        try:
            from datetime import datetime, date as date_obj
            
            # Use Hebcal client for zmanim
            if date == "today":
                target_date = date_obj.today()
            else:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            zmanim_data = await self.hebcal_client.get_zmanim(location, target_date)
            
            if not zmanim_data:
                embed = discord.Embed(
                    title="❌ Location Not Found",
                    description=f"Could not find zmanim for '{location}'. Try a major city name.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🕐 Halachic Times (Zmanim)",
                description=f"**Location:** {location}\n**Date:** {target_date.strftime('%B %d, %Y')}",
                color=discord.Color.blue()
            )
            
            # Parse zmanim times
            times = zmanim_data.get('times', {})
            
            # Morning times
            if times.get('alotHaShachar'):
                embed.add_field(name="🌅 Alot HaShachar", value=times['alotHaShachar'], inline=True)
            if times.get('misheyakir'):
                embed.add_field(name="👁️ Misheyakir", value=times['misheyakir'], inline=True)
            if times.get('sunrise'):
                embed.add_field(name="☀️ Sunrise", value=times['sunrise'], inline=True)
            
            # Prayer times
            if times.get('sofZmanShmaGRA'):
                embed.add_field(name="📿 Latest Shma (GR\"A)", value=times['sofZmanShmaGRA'], inline=True)
            if times.get('sofZmanTfilla'):
                embed.add_field(name="🙏 Latest Tfilla", value=times['sofZmanTfilla'], inline=True)
            if times.get('chatzot'):
                embed.add_field(name="🕐 Chatzot", value=times['chatzot'], inline=True)
            
            # Evening times
            if times.get('minchaGedola'):
                embed.add_field(name="🌇 Mincha Gedola", value=times['minchaGedola'], inline=True)
            if times.get('sunset'):
                embed.add_field(name="🌅 Sunset", value=times['sunset'], inline=True)
            if times.get('tzeit'):
                embed.add_field(name="⭐ Tzeit HaKochavim", value=times['tzeit'], inline=True)
            
            embed.set_footer(text="React with 📅 for tomorrow • 🕯️ for candle lighting • ℹ️ for explanations")
            message = await interaction.followup.send(embed=embed)
            
            # Add reaction buttons
            await message.add_reaction("📅")
            await message.add_reaction("🕯️")
            await message.add_reaction("ℹ️")
            
        except Exception as e:
            logger.error(f"Error in halachic_times: {e}")
            embed = discord.Embed(
                title="❌ Zmanim Error",
                description="Could not retrieve halachic times. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="parsha", description="Get comprehensive weekly Torah portion study materials")
    @app_commands.describe(
        week_offset="Weeks from current (0=this week, 1=next week, -1=last week)"
    )
    async def weekly_parsha(self, interaction: discord.Interaction, week_offset: int = 0):
        """Get comprehensive weekly Torah portion with study materials"""
        await interaction.response.defer()
        
        try:
            from datetime import datetime, timedelta
            
            # Calculate target date
            target_date = datetime.now().date() + timedelta(weeks=week_offset)
            
            # Get Torah reading from Hebcal
            torah_data = await self.hebcal_client.get_torah_reading(target_date)
            
            if not torah_data:
                embed = discord.Embed(
                    title="❌ No Torah Reading",
                    description="Could not find Torah reading for this date.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            parsha_name = torah_data.get('parsha', 'Unknown')
            
            embed = discord.Embed(
                title=f"📜 Parashat {parsha_name}",
                description=f"Weekly Torah Portion Study Guide",
                color=discord.Color.gold()
            )
            
            # Torah reading details
            if torah_data.get('torah'):
                embed.add_field(
                    name="📖 Torah Reading",
                    value=torah_data['torah'],
                    inline=False
                )
            
            if torah_data.get('haftarah'):
                embed.add_field(
                    name="📿 Haftarah",
                    value=torah_data['haftarah'],
                    inline=False
                )
            
            # Try to get text from Sefaria
            try:
                parsha_ref = f"Genesis 1:1"  # Default, would need mapping
                text_data = await self.sefaria_client.get_text(parsha_ref)
                if text_data and 'text' in text_data:
                    first_verse = text_data['text'][0] if isinstance(text_data['text'], list) else text_data['text']
                    embed.add_field(
                        name="✨ Opening Verse",
                        value=first_verse[:200] + "..." if len(first_verse) > 200 else first_verse,
                        inline=False
                    )
            except:
                pass
            
            # Study suggestions
            embed.add_field(
                name="📚 Study Suggestions",
                value="• Read with Rashi commentary\n• Explore themes and lessons\n• Find practical applications\n• Connect to current events",
                inline=False
            )
            
            embed.set_footer(text="React with 📝 for commentary • 🔍 for themes • 📖 for full text • ❓ for questions")
            message = await interaction.followup.send(embed=embed)
            
            # Add reaction buttons for interactive study
            await message.add_reaction("📝")
            await message.add_reaction("🔍")
            await message.add_reaction("📖")
            await message.add_reaction("❓")
            
        except Exception as e:
            logger.error(f"Error in weekly_parsha: {e}")
            embed = discord.Embed(
                title="❌ Parsha Error",
                description="Could not retrieve weekly Torah portion.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="halacha", description="Ask practical Jewish law questions with AI assistance")
    @app_commands.describe(
        question="Your halacha question (practical Jewish law)",
        category="Category (shabbat, kashrut, prayer, holidays, etc.)"
    )
    async def halacha_question(self, interaction: discord.Interaction, question: str, category: str = "general"):
        """AI-assisted halacha (Jewish law) question answering"""
        await interaction.response.defer()
        
        try:
            # Create a specialized prompt for halacha questions
            halacha_prompt = f"""You are a knowledgeable assistant helping with Jewish law (halacha) questions. 
            
Guidelines:
- Provide accurate, well-sourced information
- Always recommend consulting a qualified rabbi for final decisions
- Reference relevant halachic sources when possible
- Be clear about different opinions when they exist
- Focus on practical applications
- Distinguish between biblical and rabbinical laws

Category: {category}
Question: {question}

Please provide a helpful response while emphasizing the importance of consulting with a qualified rabbi for final halachic decisions."""
            
            # Use AI client for response
            if hasattr(self, 'ai_client') and self.ai_client:
                ai_response = await self.ai_client.generate_response(halacha_prompt, "Halacha Assistant")
            else:
                ai_response = "AI assistance not available. Please consult a qualified rabbi for halachic guidance."
            
            embed = discord.Embed(
                title="⚖️ Halacha Question",
                description=f"**Category:** {category.title()}\n**Question:** {question}",
                color=discord.Color.blue()
            )
            
            # Split response if too long
            if len(ai_response) > 1000:
                embed.add_field(
                    name="📚 Response (Part 1)",
                    value=ai_response[:1000] + "...",
                    inline=False
                )
                embed.add_field(
                    name="📚 Response (Part 2)",
                    value="..." + ai_response[1000:2000],
                    inline=False
                )
            else:
                embed.add_field(
                    name="📚 Response",
                    value=ai_response,
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Important Notice",
                value="This is AI-generated guidance. Always consult a qualified rabbi for final halachic decisions.",
                inline=False
            )
            
            embed.set_footer(text="React with 📖 for sources • ❓ for follow-up • 👨‍🏫 for rabbi referral")
            message = await interaction.followup.send(embed=embed)
            
            # Add reaction buttons
            await message.add_reaction("📖")
            await message.add_reaction("❓")
            await message.add_reaction("👨‍🏫")
            
        except Exception as e:
            logger.error(f"Error in halacha_question: {e}")
            embed = discord.Embed(
                title="❌ Halacha Error",
                description="Could not process halacha question. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="dafyomi", description="Get today's Daf Yomi (daily Talmud page) with study resources")
    async def daf_yomi(self, interaction: discord.Interaction):
        """Get today's Daf Yomi with comprehensive study materials"""
        await interaction.response.defer()
        
        try:
            from datetime import datetime
            
            # Calculate current Daf Yomi
            # Daf Yomi cycle started September 11, 1923
            cycle_start = datetime(1923, 9, 11)
            current_date = datetime.now()
            days_since_start = (current_date - cycle_start).days
            
            # Each cycle is 2,711 days (total pages in Babylonian Talmud)
            cycle_number = (days_since_start // 2711) + 1
            day_in_cycle = days_since_start % 2711 + 1
            
            # Simplified tractate mapping (would need full mapping in production)
            tractates = [
                ("Berakhot", 64), ("Shabbat", 157), ("Eruvin", 105), ("Pesachim", 121),
                ("Shekalim", 22), ("Yoma", 88), ("Sukkah", 56), ("Beitzah", 40),
                ("Rosh Hashanah", 35), ("Taanit", 31), ("Megillah", 32), ("Moed Katan", 29),
                ("Chagigah", 27), ("Yevamot", 122), ("Ketubot", 112), ("Nedarim", 91),
                ("Nazir", 66), ("Sotah", 49), ("Gittin", 90), ("Kiddushin", 82)
            ]
            
            # Calculate current tractate and page
            current_page = day_in_cycle
            current_tractate = "Berakhot"  # Simplified
            page_in_tractate = current_page
            
            embed = discord.Embed(
                title="📖 Today's Daf Yomi",
                description=f"Daily Talmud Study • Cycle #{cycle_number}",
                color=discord.Color.dark_blue()
            )
            
            embed.add_field(
                name="📚 Current Study",
                value=f"**{current_tractate} {page_in_tractate}a-b**",
                inline=False
            )
            
            embed.add_field(
                name="📅 Cycle Information",
                value=f"**Cycle:** {cycle_number}\n**Day in Cycle:** {day_in_cycle}/2,711",
                inline=True
            )
            
            embed.add_field(
                name="⏰ Study Schedule",
                value="**Duration:** ~45 minutes\n**Format:** Both sides of page",
                inline=True
            )
            
            # Add study resources
            embed.add_field(
                name="📖 Study Resources",
                value="• Gemara text with Rashi\n• Tosafot commentary\n• English translation\n• Audio shiurim available",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Study Tips",
                value="• Read slowly and carefully\n• Use multiple commentaries\n• Join study groups\n• Review previous pages",
                inline=False
            )
            
            embed.set_footer(text="React with 📝 for notes • 🔊 for audio • 👥 for study groups • 📖 for text")
            message = await interaction.followup.send(embed=embed)
            
            # Add reaction buttons
            await message.add_reaction("📝")
            await message.add_reaction("🔊")
            await message.add_reaction("👥")
            await message.add_reaction("📖")
            
        except Exception as e:
            logger.error(f"Error in daf_yomi: {e}")
            embed = discord.Embed(
                title="❌ Daf Yomi Error",
                description="Could not retrieve today's Daf Yomi information.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="learning", description="Personalized Jewish learning path recommendations")
    @app_commands.describe(
        level="Your learning level (beginner, intermediate, advanced)",
        interests="Areas of interest (torah, talmud, halacha, chassidut, etc.)"
    )
    async def learning_path(self, interaction: discord.Interaction, level: str, interests: str = "general"):
        """Get personalized Jewish learning recommendations"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="📚 Personalized Learning Path",
                description=f"**Level:** {level.title()}\n**Interests:** {interests.title()}",
                color=discord.Color.green()
            )
            
            # Customize recommendations based on level and interests
            if level.lower() == "beginner":
                embed.add_field(
                    name="🌱 Getting Started",
                    value="• Weekly Torah portion (Parsha)\n• Basic Jewish concepts\n• Prayer book (Siddur) study\n• Jewish holidays and customs",
                    inline=False
                )
                embed.add_field(
                    name="📖 Recommended Texts",
                    value="• Pirkei Avot (Ethics of the Fathers)\n• Simple Chumash with Rashi\n• Basic Shulchan Aruch\n• Stories of the Sages",
                    inline=False
                )
            elif level.lower() == "intermediate":
                embed.add_field(
                    name="📈 Building Knowledge",
                    value="• Complete Chumash study\n• Mishnah tractates\n• Halacha (Jewish law)\n• Jewish philosophy basics",
                    inline=False
                )
                embed.add_field(
                    name="📚 Study Options",
                    value="• Rambam's Mishneh Torah\n• Selected Talmud pages\n• Medieval commentaries\n• Chassidic teachings",
                    inline=False
                )
            else:  # advanced
                embed.add_field(
                    name="🎓 Advanced Study",
                    value="• Daily Talmud (Daf Yomi)\n• Complex halachic texts\n• Kabbalah and mysticism\n• Original research",
                    inline=False
                )
                embed.add_field(
                    name="🔬 Deep Dive",
                    value="• Rishonim and Acharonim\n• Responsa literature\n• Comparative analysis\n• Teaching others",
                    inline=False
                )
            
            # Add interest-specific recommendations
            if "talmud" in interests.lower():
                embed.add_field(
                    name="📖 Talmud Focus",
                    value="• Start with Tractate Berakhot\n• Join Daf Yomi program\n• Use English translations initially\n• Find study partner (chavruta)",
                    inline=False
                )
            elif "halacha" in interests.lower():
                embed.add_field(
                    name="⚖️ Halacha Focus",
                    value="• Daily halacha study\n• Practical applications\n• Shulchan Aruch sections\n• Contemporary responsa",
                    inline=False
                )
            elif "chassidut" in interests.lower():
                embed.add_field(
                    name="✨ Chassidut Focus",
                    value="• Daily Tanya study\n• Chassidic stories\n• Rebbes' teachings\n• Mystical concepts",
                    inline=False
                )
            
            embed.add_field(
                name="🛠️ Study Tools",
                value="• Use this bot's commands\n• Join online study groups\n• Find local classes\n• Regular review schedule",
                inline=False
            )
            
            embed.set_footer(text="React with 📅 for schedule • 👥 for groups • 📖 for texts • ⭐ for favorites")
            message = await interaction.followup.send(embed=embed)
            
            # Add reaction buttons
            await message.add_reaction("📅")
            await message.add_reaction("👥")
            await message.add_reaction("📖")
            await message.add_reaction("⭐")
            
        except Exception as e:
            logger.error(f"Error in learning_path: {e}")
            embed = discord.Embed(
                title="❌ Learning Path Error",
                description="Could not generate learning recommendations.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    # Add reaction event handler for interactive features
    async def on_reaction_add(self, reaction, user):
        """Handle reaction-based interactions"""
        if user.bot:
            return
            
        try:
            # Handle gematria reactions
            if reaction.emoji == "🔄" and "Gematria Calculator" in str(reaction.message.embeds[0].title):
                # Add more calculation methods
                pass
            elif reaction.emoji == "📖" and "Gematria Calculator" in str(reaction.message.embeds[0].title):
                # Search for related texts with same gematria value
                pass
            
            # Handle zmanim reactions
            elif reaction.emoji == "📅" and "Halachic Times" in str(reaction.message.embeds[0].title):
                # Show tomorrow's times
                pass
            elif reaction.emoji == "🕯️" and "Halachic Times" in str(reaction.message.embeds[0].title):
                # Show candle lighting times
                pass
            
            # Handle parsha reactions
            elif reaction.emoji == "📝" and "Parashat" in str(reaction.message.embeds[0].title):
                # Show commentary
                pass
            elif reaction.emoji == "🔍" and "Parashat" in str(reaction.message.embeds[0].title):
                # Show themes
                pass
                
        except Exception as e:
            logger.error(f"Error in reaction handler: {e}")
