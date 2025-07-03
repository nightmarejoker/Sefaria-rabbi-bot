# Sefaria Discord Bot

## Overview

This is a Discord bot that integrates with the Sefaria API to provide access to Jewish texts directly within Discord servers. The bot allows users to retrieve random quotes from Jewish texts, with support for both Hebrew and English languages. It's built using Python with the discord.py library and implements asynchronous operations for optimal performance.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Main Entry Point** (`main.py`): Handles bot initialization, startup, and web server for health checks
- **Bot Core** (`bot/discord_bot.py`): Main bot class extending discord.py's commands.Bot
- **Command Handler** (`bot/commands.py`): Discord slash commands implementation
- **API Client** (`bot/sefaria_client.py`): Sefaria API integration with rate limiting
- **AI Client** (`bot/ai_client.py`): OpenAI integration for conversational AI responses
- **Utilities** (`bot/utils.py`): Text formatting and processing helpers

The architecture prioritizes:
- Hybrid deployment supporting both Discord bot and web health checks
- Asynchronous operations for non-blocking API calls
- Rate limiting to respect Sefaria API constraints
- Error handling and logging throughout the system
- Modular design for easy maintenance and extension

## Key Components

### Discord Bot (`SefariaBot`)
- Extends `discord.py` commands.Bot
- Configures necessary intents for message content access
- Handles bot lifecycle events (startup, ready state)
- Manages slash command synchronization

### Sefaria API Client (`SefariaClient`)
- Manages HTTP sessions using aiohttp
- Implements rate limiting (1 second between requests)
- Handles API authentication and request formatting
- Provides error handling and retry logic

### Command System (`SefariaCommands`)
- Implements Discord slash commands using app_commands
- Supports language preferences (Hebrew, English, both)
- Provides text category filtering
- Formats responses using Discord embeds

### Text Processing (`utils.py`)
- Cleans HTML tags from API responses
- Truncates text to fit Discord's character limits
- Formats bilingual text display
- Creates styled Discord embeds

## Data Flow

1. **User Interaction**: User invokes slash command in Discord
2. **Command Processing**: Bot receives command and validates parameters
3. **API Request**: Sefaria client makes rate-limited request to Sefaria API
4. **Response Processing**: Text data is cleaned and formatted
5. **Display**: Formatted embed is sent back to Discord channel

The flow implements proper error handling at each stage, with fallback responses for API failures.

## External Dependencies

### Core Dependencies
- **discord.py**: Discord API wrapper for bot functionality
- **aiohttp**: Asynchronous HTTP client for Sefaria API calls
- **python-dotenv**: Environment variable management

### External Services
- **Sefaria API**: Primary data source for Jewish texts
  - Base URL: `https://www.sefaria.org/api`
  - Rate limited to 1 request per second
  - No authentication required for public endpoints

### Environment Requirements
- **DISCORD_TOKEN**: Required Discord bot token for authentication
- **Python 3.7+**: Async/await support required

## Deployment Strategy

The application is designed for hybrid deployment supporting both Discord bot functionality and web service requirements:

### Web Server Integration
- HTTP health check endpoints at `/` and `/health`
- Serves on port 5000 (0.0.0.0 binding for external access)
- JSON responses for deployment platform health checks
- Concurrent operation with Discord bot services

### Environment Setup
- Load environment variables from `.env` file
- Discord token must be provided via `DISCORD_TOKEN` environment variable
- PORT environment variable supported (defaults to 5000)

### Logging Configuration
- Dual logging to both file (`sefaria_bot.log`) and console
- INFO level logging for operational visibility
- Structured error handling with detailed logging
- Web server access logging included

### Process Management
- Graceful shutdown handling for SIGINT
- Async context management for proper resource cleanup
- Session management for HTTP connections
- Concurrent task management for web server and Discord bot

## Changelog

- July 03, 2025. Initial setup
- July 03, 2025. Added AI conversation capabilities with OpenAI GPT-3.5-turbo integration
- July 03, 2025. Implemented @mention handling for natural conversations
- July 03, 2025. Added /setprompt command for customizing AI behavior
- July 03, 2025. Fixed deployment issues by adding web server with health check endpoints
- July 03, 2025. Fixed duplicate message responses by removing test workflow and adding message deduplication

## User Preferences

Preferred communication style: Simple, everyday language.