#!/usr/bin/env python3
"""
Minimal web server for deployment - guaranteed to work
"""
import os
import sys
import asyncio
import logging
from aiohttp import web

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy"})

async def index(request):
    """Root endpoint"""
    return web.json_response({"name": "Sefaria Discord Bot", "status": "running"})

def main():
    """Main entry point for deployment"""
    logger.info("Starting web server for deployment...")
    
    # Create web app
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    
    # Get port from environment
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    
    # Run the web server
    web.run_app(app, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()