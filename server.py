#!/usr/bin/env python3
"""
Minimal web server for deployment health checks
"""
import os
import sys
import subprocess
from aiohttp import web
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "service": "Sefaria Discord Bot"})

async def index(request):
    """Root endpoint"""
    return web.json_response({
        "name": "Sefaria Discord Bot", 
        "status": "running",
        "description": "Discord bot for Jewish texts"
    })

def install_deps():
    """Install dependencies"""
    deps = ["aiohttp>=3.12.13", "discord.py>=2.5.2", "python-dotenv>=1.1.1", "openai>=1.93.0"]
    for dep in deps:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except:
            pass

async def main():
    """Main function"""
    logger.info("Installing dependencies...")
    install_deps()
    
    logger.info("Starting web server...")
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', health_check)
    
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Server starting on port {port}")
    
    # Start Discord bot in background
    try:
        from bot.discord_bot import SefariaBot
        token = os.getenv('DISCORD_TOKEN')
        if token:
            bot = SefariaBot()
            asyncio.create_task(bot.start(token))
            logger.info("Discord bot started")
    except Exception as e:
        logger.warning(f"Discord bot failed: {e}")
    
    # Run web server
    return await web._run_app(app, host='0.0.0.0', port=port)

if __name__ == "__main__":
    asyncio.run(main())