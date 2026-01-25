# Roblox Moderation System

## Overview

This is a Discord bot integrated with a Flask API server designed for moderating Roblox game servers. The system allows Discord users with specific roles to execute moderation commands (like bans) that are then polled by Roblox game servers. The architecture follows a command queue pattern where Discord acts as the command input interface, Flask serves as the intermediary API, and Roblox game servers consume the commands.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Dual-Service Architecture
- **Discord Bot** (`bot.py`): Handles user interactions through Discord slash commands. Uses discord.py with the commands extension and app_commands for slash command support.
- **Flask API Server** (`server.py`): Lightweight REST API that stores commands in memory and serves them to external consumers (Roblox game servers).

### Entry Point
- `main.py` orchestrates both services, running Flask in a background daemon thread while the Discord bot runs in the main thread.

### Command Flow Pattern
1. Discord users with allowed roles issue commands via the bot
2. Bot sends commands to the Flask API (`/send_command` endpoint)
3. Roblox game servers poll `/get_commands` to retrieve pending commands
4. Commands can be cleared via `/clear_commands`

### Role-Based Access Control
- Uses Discord role IDs (`ALLOWED_ROLE_ID`, `ADMIN_ROLE_ID`) to restrict who can execute moderation commands
- Role IDs are configured via environment variables

### Data Storage
- **In-Memory Storage**: Commands, player counts, banned user IDs, and blacklisted asset IDs are stored in Python lists/sets (non-persistent)
- **File-Based Ban Lists**: JSON and TXT exports of ban lists are saved to the `banlists/` directory

### External API Integration
- The bot communicates with an external API (`API_URL`) for asset blacklist management, suggesting this system may be part of a larger infrastructure

## External Dependencies

### Discord Integration
- **discord.py**: Core Discord API wrapper for bot functionality
- **DISCORD_TOKEN**: Required environment variable for bot authentication

### Web Framework
- **Flask**: Serves the REST API on port 5000
- Used for command queue management and player tracking

### External Services
- **Roblox API** (implied): The system is designed to moderate Roblox game servers
- **External Blacklist API**: Asset blacklist checking via remote API endpoint

### Environment Variables Required
- `DISCORD_TOKEN`: Discord bot authentication token
- `ALLOWED_ROLE_ID`: Discord role ID for basic moderation access
- `ADMIN_ROLE_ID`: Discord role ID for administrative access

### Key Python Packages
- `discord.py` - Discord bot framework
- `Flask` - Web API server
- `requests` - HTTP client for external API calls
- `python-dotenv` - Environment variable management
- `pynacl` - Cryptography for Discord voice (if needed)