# Roblox Moderation System

## Overview

This is a Roblox game moderation system that bridges Discord and Roblox. It consists of a Discord bot for moderators to issue commands (bans, kicks, etc.) and a Flask API server that communicates with Roblox game servers. The system allows Discord-based moderation of Roblox players, with features like ban lists, player tracking, and persistent ban storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**Discord Bot (`bot.py`)**
- Built with discord.py library using slash commands (app_commands)
- Implements role-based access control with ALLOWED_ROLE_ID and ADMIN_ROLE_ID
- Features confirmation dialogs for moderation actions using Discord UI Views
- Creates formatted embeds for moderation notifications
- Supports 19 moderation commands including ban types (normal, PC ban)

**Flask API Server (`server.py`)**
- Lightweight REST API for Roblox game server communication
- Endpoints for command queue management (`/send_command`, `/get_commands`, `/clear_commands`)
- Player count tracking (`/update_players`, `/get_players`)
- In-memory storage for commands and banned user IDs
- Runs on port 5000

**Main Entry Point (`main.py`)**
- Orchestrates both Flask server and Discord bot
- Implements retry logic for Discord rate limits (429 errors)
- Environment variable validation
- Threaded execution for concurrent bot and server operation

### Data Flow

1. Moderator issues command via Discord slash command
2. Bot validates permissions and shows confirmation dialog
3. On confirmation, command is sent to Flask API
4. Roblox game server polls `/get_commands` endpoint
5. Game server executes moderation action and clears commands

### Persistence

**Ban Lists (`banlists/` directory)**
- Automatic saving of ban records
- Dual format storage: JSON (machine-readable) and TXT (human-readable)
- Contains metadata (timestamp, total bans, server info) and ban details
- File naming convention: `banlist_YYYYMMDD_HHMMSS.{json|txt}`

### Authentication & Authorization

- Discord bot uses token-based authentication via DISCORD_TOKEN
- Role-based permission system with two tiers:
  - ALLOWED_ROLE_ID: Standard moderator access
  - ADMIN_ROLE_ID: Administrative privileges
- API endpoints are currently unauthenticated (designed for internal/local network use)

## External Dependencies

### Third-Party Services

- **Discord API**: Bot hosting and slash command framework
- **Roblox API**: Referenced via API_URL constant for user lookups

### Python Libraries

- `discord.py`: Discord bot framework with UI components
- `Flask`: REST API server
- `python-dotenv`: Environment variable management
- `requests`: HTTP client for external API calls

### Environment Variables Required

| Variable | Purpose |
|----------|---------|
| DISCORD_TOKEN | Bot authentication token |
| ALLOWED_ROLE_ID | Discord role ID for moderator access |
| ADMIN_ROLE_ID | Discord role ID for admin access |

### External Integration Points

- Roblox game servers poll the Flask API for moderation commands
- Bot communicates with Roblox API for user information lookups
- Commands are queued in-memory and consumed by game servers