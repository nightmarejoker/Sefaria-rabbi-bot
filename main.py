#!/usr/bin/env python3
"""
Main entry point for the Sefaria Discord Bot
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from bot.discord_bot import SefariaBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sefaria_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Discord bot"""
    try:
        # Get Discord token from environment
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            logger.error("DISCORD_TOKEN not found in environment variables")
            return

        # Create and start the bot
        bot = SefariaBot()
        await bot.start(discord_token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Bot shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
