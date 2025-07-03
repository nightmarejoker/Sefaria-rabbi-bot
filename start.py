#!/usr/bin/env python3
"""
Deployment startup script for Sefaria Discord Bot
Ensures dependencies are installed and starts the application
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        "discord.py>=2.5.2",
        "python-dotenv>=1.1.1", 
        "aiohttp>=3.12.13",
        "openai>=1.93.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {dep}: {e}")

def main():
    """Main startup function"""
    print("Installing dependencies...")
    install_dependencies()
    
    print("Starting Sefaria Discord Bot...")
    
    # Import and run the main application
    try:
        from main import main as app_main
        import asyncio
        asyncio.run(app_main())
    except ImportError as e:
        print(f"Import error: {e}")
        # Fallback: run main.py directly
        subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()