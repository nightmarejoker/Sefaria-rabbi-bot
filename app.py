#!/usr/bin/env python3
"""
Simple web server entry point for deployment
"""
import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "Sefaria Discord Bot",
        "version": "1.0.0"
    })

async def index(request):
    """Root endpoint"""
    return web.json_response({
        "name": "Sefaria Discord Bot",
        "description": "Discord bot for Jewish texts from Sefaria",
        "status": "running",
        "endpoints": {"/": "Info", "/health": "Health check"}
    })

async def create_app():
    """Create web application"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', health_check)
    return app

async def start_bot_in_background():
    """Start Discord bot in background"""
    try:
        # Import and start Discord bot
        from bot.discord_bot import SefariaBot
        discord_token = os.getenv('DISCORD_TOKEN')
        if discord_token:
            bot = SefariaBot()
            asyncio.create_task(bot.start(discord_token))
            logger.info("Discord bot started in background")
        else:
            logger.warning("No Discord token found - running web server only")
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        logger.info("Continuing with web server only")

async def main():
    """Main function"""
    # Start Discord bot in background (optional)
    await start_bot_in_background()
    
    # Create and start web server
    app = await create_app()
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"Starting web server on port {port}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Server running on http://0.0.0.0:{port}")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())