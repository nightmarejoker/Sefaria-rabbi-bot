#!/usr/bin/env python3
"""
Deployment entry point - installs deps and starts web server
"""
import subprocess
import sys
import os

def main():
    print("Starting deployment...")
    
    # Install dependencies
    print("Installing dependencies...")
    deps = ["aiohttp", "discord.py", "python-dotenv", "openai"]
    for dep in deps:
        subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                      capture_output=True)
    
    # Start the main application
    print("Starting application...")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()