#!/bin/bash
# Deployment startup script for Sefaria Discord Bot

echo "Starting Sefaria Discord Bot deployment..."

# Install dependencies if needed
echo "Installing dependencies..."
pip install aiohttp>=3.12.13 discord.py>=2.5.2 openai>=1.93.0 python-dotenv>=1.1.1

# Start the application
echo "Starting application..."
python app.py