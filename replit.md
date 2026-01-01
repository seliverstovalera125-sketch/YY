# Roblox Moderation System

## Overview

This is a Roblox game moderation system that bridges Discord and Roblox. It allows server moderators to issue commands (bans, kicks, etc.) through Discord slash commands, which are then relayed to Roblox game servers via a REST API. The system consists of two main components running concurrently: a Discord bot for moderator interaction and a Flask API server that acts as a command relay.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Dual-Process Architecture
The application runs two services simultaneously using Python threading:
- **Discord Bot** (`bot.py`): Handles moderator commands via Discord slash commands using discord.py
- **Flask API Server** (`server.py`): Provides REST endpoints for Roblox game servers to poll for commands

The `main.py` file orchestrates both services, starting Flask in a daemon thread while the Discord bot runs in the main thread.

### Command Flow Pattern
1. Moderator issues a slash command in Discord (e.g., `/ban`)
2. Discord bot validates permissions (role-based: ALLOWED_ROLE_ID, ADMIN_ROLE_ID)
3. Bot presents a confirmation UI using Discord's View/Button components
4. Upon confirmation, bot POSTs the command to the Flask API
5. Roblox game servers poll `/get_commands` endpoint periodically
6. After fetching, servers call `/clear_commands` to acknowledge

### Data Storage
- **In-Memory Command Queue**: Commands stored in a Python list, cleared after Roblox fetches them
- **Banned Users Set**: In-memory set tracking banned user IDs for quick lookups
- **File-Based Banlist Persistence**: Ban records exported to `banlists/` directory in both JSON and TXT formats with timestamps

### Authentication & Authorization
- Discord role-based permissions using environment variables:
  - `ALLOWED_ROLE_ID`: Standard moderator access
  - `ADMIN_ROLE_ID`: Elevated admin privileges
- No API authentication between Flask and Roblox (relies on network security)

### UI Components
- Custom `ModerationEmbed` class for consistent Discord embed formatting
- `ConfirmActionView` for interactive confirmation dialogs with timeout

## External Dependencies

### Third-Party Services
- **Discord API**: Bot integration via discord.py library with slash commands (app_commands)
- **Roblox Game Servers**: External clients that poll the Flask API for moderation commands

### Python Packages
- `discord.py`: Discord bot framework with slash command support
- `Flask`: Lightweight REST API server
- `python-dotenv`: Environment variable management
- `requests`: HTTP client for API calls

### Environment Variables Required
- `DISCORD_TOKEN`: Bot authentication token (required)
- `ALLOWED_ROLE_ID`: Discord role ID for moderator access
- `ADMIN_ROLE_ID`: Discord role ID for admin access

### External API Reference
The bot connects to an external API at a Replit URL for additional functionality (referenced as `API_URL` in bot.py).

### File System
- `banlists/` directory: Stores persistent ban records as timestamped JSON and TXT files