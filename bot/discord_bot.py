"""
Main Discord bot class for Sefaria integration
"""
import discord
from discord.ext import commands
import logging
from .commands import SefariaCommands
from .sefaria_client import SefariaClient

logger = logging.getLogger(__name__)

class SefariaBot(commands.Bot):
    """Discord bot for Sefaria Jewish texts"""
    
    def __init__(self):
        # Configure intents - using default intents only (no privileged intents needed)
        intents = discord.Intents.default()
        # Remove privileged intent that requires special permission
        # intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="A Discord bot for accessing Jewish texts from Sefaria"
        )
        
        # Initialize Sefaria client
        self.sefaria_client = SefariaClient()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Add the cog
            await self.add_cog(SefariaCommands(self, self.sefaria_client))
            
            # Sync slash commands
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="Jewish wisdom | /sefaria help"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        logger.error(f"Command error: {error}")
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument. Use `/sefaria help` for usage information.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            await ctx.send("❌ An error occurred while processing your command.")
    
    async def on_error(self, event, *args, **kwargs):
        """Global error handler for events"""
        logger.error(f"An error occurred in event {event}", exc_info=True)
