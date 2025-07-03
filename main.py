#!/usr/bin/env python3
"""
Main entry point for the Sefaria Discord Bot with web server for health checks
"""
import asyncio
import logging
import os
from aiohttp import web
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

async def health_check(request):
    """Health check endpoint for deployment platform"""
    return web.json_response({
        "status": "healthy",
        "service": "Sefaria Discord Bot",
        "version": "1.0.0"
    })

async def index(request):
    """Root endpoint showing bot information"""
    return web.json_response({
        "name": "Sefaria Discord Bot",
        "description": "A Discord bot that integrates with the Sefaria API to provide access to Jewish texts",
        "status": "running",
        "endpoints": {
            "/": "Bot information",
            "/health": "Health check"
        }
    })

async def create_web_app():
    """Create the web application for health checks"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', health_check)  # Alternative health check endpoint
    return app

async def start_web_server():
    """Start the web server for health checks"""
    app = await create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Use port 5000 as required by Replit
    port = int(os.getenv('PORT', 5000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port}")
    return runner

async def start_discord_bot():
    """Start the Discord bot"""
    # Get Discord token from environment
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return None

    # Create and start the bot
    bot = SefariaBot()
    
    # Start bot in background task
    bot_task = asyncio.create_task(bot.start(discord_token))
    logger.info("Discord bot started")
    return bot_task, bot

async def main():
    """Main function to start both web server and Discord bot"""
    web_runner = None
    bot = None
    
    try:
        # Start web server for health checks first (critical for deployment)
        web_runner = await start_web_server()
        
        # Start Discord bot (optional - web server should stay up even if bot fails)
        bot_result = await start_discord_bot()
        if bot_result is None:
            logger.warning("Discord bot failed to start, but web server will continue running")
            # Keep web server running indefinitely for health checks
            try:
                while True:
                    await asyncio.sleep(60)  # Keep alive
            except KeyboardInterrupt:
                logger.info("Application shutdown requested by user")
            return
        
        bot_task, bot = bot_result
        logger.info("Both web server and Discord bot are running")
        
        # Keep the application running
        try:
            await bot_task
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            # Even if bot fails, keep web server running
            logger.info("Keeping web server running for health checks")
            try:
                while True:
                    await asyncio.sleep(60)  # Keep alive
            except KeyboardInterrupt:
                logger.info("Application shutdown requested by user")
        
    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Application shutting down...")
        try:
            if web_runner:
                await web_runner.cleanup()
            if bot:
                await bot.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
