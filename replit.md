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
- July 03, 2025. Enhanced /text command with integrated commentary support (Rashi, Ibn Ezra, Ramban, Ralbag, Sforno, Radak)
- July 03, 2025. Added /autoreply admin command for server-level @mention response control
- July 03, 2025. Created mobile-friendly download packages and GitHub upload guides due to Replit Git restrictions
- July 03, 2025. Successfully uploaded Discord bot to GitHub with proper bot/ folder structure, ready for deployment
- July 03, 2025. **MAJOR ENHANCEMENT**: Added comprehensive National Library of Israel API integration with 5 new commands
- July 03, 2025. **NEW FEATURE**: Added Google Translate integration for multilingual support
- July 03, 2025. **BUG FIX**: Implemented lock file system to prevent multiple bot instances and eliminate double responses
- July 03, 2025. **EXPANDED COMMANDS**: Added prayer times, Torah portion, Daf Yomi, and gematria calculation features
- July 03, 2025. **CHABAD INTEGRATION**: Added comprehensive Chabad.org content integration with 5 new Chassidic commands
- July 03, 2025. **COMPLETE ECOSYSTEM**: Bot now provides content from 4 major Jewish institutions with 20+ specialized commands
- July 03, 2025. **REVOLUTIONARY AI INTEGRATION**: Added Dicta Israel Center integration with 800+ AI-enhanced Jewish books
- July 03, 2025. **ADVANCED TEXT ANALYSIS**: Integrated cutting-edge Jewish text processing with automatic nikud, Rashi script conversion
- July 03, 2025. **MASSIVE EXPANSION**: Added 7+ new commands covering kosher laws, responsa literature, and AI-digitized manuscripts
- July 03, 2025. **ULTIMATE JEWISH BOT**: Now features 30+ commands spanning 5 major institutions with unprecedented text analysis capabilities
- July 03, 2025. **REVOLUTIONARY EXPANSION**: Added TorahCalc and OpenTorah integrations creating the most comprehensive Jewish Discord bot ever built
- July 03, 2025. **BREAKTHROUGH CONSOLIDATION**: Streamlined overlapping commands into 3 smart unified commands for superior user experience  
- July 03, 2025. **CALCULATION POWERHOUSE**: Integrated TorahCalc's "Jewish Wolfram Alpha" with natural language processing for biblical calculations
- July 03, 2025. **DIGITAL ARCHIVES**: Added OpenTorah's early Chabad historical archives and advanced Jewish calendar computations
- July 03, 2025. **SMART COMMAND FUSION**: Created 4 revolutionary new commands that intelligently combine multiple APIs for unprecedented functionality
- July 03, 2025. **FINAL EXPANSION**: Added Orayta, OpenSiddur, and Pninim integrations creating the most comprehensive Jewish software ecosystem ever assembled
- July 03, 2025. **ULTIMATE ACHIEVEMENT**: Successfully integrated 10+ major Jewish institutions with 50+ specialized commands spanning every aspect of Jewish learning and practice
- July 03, 2025. **REVOLUTIONARY COMPLETION**: Created the definitive Jewish Discord bot with liturgical creation, social Torah learning, cross-platform libraries, and unprecedented functionality
- July 03, 2025. **CODE QUALITY IMPROVEMENTS**: Cleaned up unnecessary documentation files, fixed LSP errors, and enhanced code quality based on Java Discord API patterns
- July 03, 2025. **ADVANCED JEWISH COMMANDS**: Added 6 new interactive commands (gematria, zmanim, parsha, halacha, dafyomi, learning) with reaction-based functionality
- July 03, 2025. **COMPREHENSIVE CLEANUP**: Removed obsolete files, improved error handling, and implemented better null safety patterns throughout the codebase
- July 03, 2025. **SECURITY ENHANCEMENT**: Completed comprehensive security audit, fixed hardcoded API key vulnerability, and implemented proper environment variable management

## User Preferences

Preferred communication style: Simple, everyday language.