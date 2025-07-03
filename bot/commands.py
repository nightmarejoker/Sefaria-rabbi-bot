"""
Discord commands for Sefaria integration
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from typing import Optional
from .sefaria_client import SefariaClient
from .hebcal_client import HebcalClient
from .utils import format_text_response, truncate_text
from datetime import date

logger = logging.getLogger(__name__)

class SefariaCommands(commands.Cog):
    """Cog containing all Sefaria-related commands"""
    
    def __init__(self, bot, sefaria_client: SefariaClient):
        self.bot = bot
        self.sefaria_client = sefaria_client
        self.hebcal_client = HebcalClient()
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
            embed = format_text_response(text_data, language)
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
                    # Format the commentary reference
                    formatted_ref = reference.replace(" ", "_").replace(":", ".")
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
        # Check if user has admin permissions
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
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
    
    @app_commands.command(name="help", description="Show help information for Sefaria bot commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information"""
        embed = discord.Embed(
            title="📚 Sefaria Bot Help",
            description="Access Jewish texts and wisdom from the Sefaria library",
            color=discord.Color.blue()
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
            name="ℹ️ Data Sources",
            value="Texts: Sefaria.org • Calendar: Hebcal.com",
            inline=False
        )
        
        embed.set_footer(text="Bot created with ❤️ for Torah study")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="categories", description="List available text categories")
    async def list_categories(self, interaction: discord.Interaction):
        """List available text categories"""
        await interaction.response.defer()
        
        try:
            categories = await self.sefaria_client.get_categories()
            
            if not categories:
                embed = discord.Embed(
                    title="❌ No Categories",
                    description="Could not retrieve category list.",
                    color=discord.Color.red()
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
            
        except Exception as e:
            logger.error(f"Error in list_categories: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching categories.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="setprompt", description="Set the AI system prompt (admin only)")
    @app_commands.describe(prompt="The new system prompt for the AI")
    async def set_ai_prompt(self, interaction: discord.Interaction, prompt: str):
        """Set the AI system prompt"""
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
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
