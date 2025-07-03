# Sefaria Discord Bot

A Discord bot that integrates with the Sefaria API to provide access to Jewish texts directly within Discord servers. Users can retrieve random quotes, search for specific texts, and get daily Torah portions with support for both Hebrew and English languages.

## Features

- **Random Quotes**: Get random quotes from Jewish texts
- **Text Search**: Search for specific texts and passages
- **Daily Texts**: Access daily Torah portions and study materials
- **AI Conversations**: Chat with the bot using OpenAI integration
- **Bilingual Support**: Hebrew and English text display
- **Slash Commands**: Modern Discord slash command interface

## Available Commands

- `/random` - Get a random quote from Jewish texts
- `/search` - Search for specific texts
- `/text` - Get a specific text by reference
- `/daily` - Get today's Torah portion
- `/categories` - List available text categories
- `/help` - Show help information
- `/setprompt` - Set AI system prompt (for conversations)

## Setup

### Prerequisites

- Python 3.11 or higher
- Discord Bot Token
- OpenAI API Key (optional, for AI features)

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your tokens:
   ```bash
   DISCORD_TOKEN=your_discord_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Deployment

This bot is designed for easy deployment on various platforms:

### Heroku
1. Push to GitHub
2. Connect GitHub repo to Heroku
3. Set environment variables in Heroku dashboard
4. Deploy using the included `Procfile`

### Railway/Render
1. Connect GitHub repo
2. Set environment variables
3. Deploy automatically

## Environment Variables

- `DISCORD_TOKEN` - Your Discord bot token (required)
- `OPENAI_API_KEY` - OpenAI API key for AI features (optional)
- `PORT` - Port for web server (default: 5000)

## Project Structure

```
├── bot/                    # Bot modules
│   ├── discord_bot.py     # Main bot class
│   ├── commands.py        # Discord commands
│   ├── sefaria_client.py  # Sefaria API integration
│   ├── ai_client.py       # OpenAI integration
│   └── utils.py           # Utility functions
├── main.py                # Application entry point
├── Procfile               # Deployment configuration
├── pyproject.toml         # Python dependencies
└── .env.example           # Environment variables template
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.# Sefaria-rabbi-bot
