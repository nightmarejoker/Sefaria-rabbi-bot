#!/usr/bin/env python3
"""
Entry point for Replit deployment system
This file is specifically designed to work with Replit's $file variable system
"""
import os
import sys
import asyncio
import logging
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for deployment"""
    return web.json_response({
        "status": "healthy",
        "service": "Sefaria Discord Bot",
        "version": "1.0.0"
    })

async def index(request):
    """Root endpoint with bot information"""
    return web.json_response({
        "name": "Sefaria Discord Bot",
        "description": "A Discord bot that integrates with the Sefaria API to provide access to Jewish texts",
        "status": "running",
        "endpoints": {
            "/": "Bot information",
            "/health": "Health check"
        }
    })

async def start_discord_bot():
    """Start Discord bot in background"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import and start bot
        from bot.discord_bot import SefariaBot
        
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            logger.warning("DISCORD_TOKEN not found - running web server only")
            return
        
        bot = SefariaBot()
        asyncio.create_task(bot.start(discord_token))
        logger.info("Discord bot started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        logger.info("Continuing with web server only")

async def main():
    """Main application entry point"""
    logger.info("Starting Sefaria Discord Bot for deployment...")
    
    # Start Discord bot in background
    await start_discord_bot()
    
    # Create web application
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', health_check)
    
    # Get port from environment (deployment systems set this)
    port = int(os.getenv('PORT', 8080))  # Use 8080 as fallback for deployment
    
    logger.info(f"Starting web server on port {port}")
    
    # Run web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Server running on http://0.0.0.0:{port}")
    logger.info("Application ready for deployment")
    
    # Keep the application running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())