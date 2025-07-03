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
from .utils import format_text_response, truncate_text

logger = logging.getLogger(__name__)

class SefariaCommands(commands.Cog):
    """Cog containing all Sefaria-related commands"""
    
    def __init__(self, bot, sefaria_client: SefariaClient):
        self.bot = bot
        self.sefaria_client = sefaria_client
        
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
    
    @app_commands.command(name="text", description="Get a specific text by reference")
    @app_commands.describe(
        reference="Text reference (e.g., 'Genesis 1:1', 'Berakhot 2a')",
        language="Language preference (hebrew, english, or both)"
    )
    async def get_text(
        self,
        interaction: discord.Interaction,
        reference: str,
        language: Optional[str] = "both"
    ):
        """Get a specific text by reference"""
        await interaction.response.defer()
        
        try:
            text_data = await self.sefaria_client.get_text(reference)
            
            if not text_data:
                embed = discord.Embed(
                    title="❌ Text Not Found",
                    description=f"Could not find text for reference: **{reference}**",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = format_text_response(text_data, language)
            await interaction.followup.send(embed=embed)
            
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
            name="ℹ️ About Sefaria",
            value="Sefaria is a free digital library of Jewish texts and their interconnections.",
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
