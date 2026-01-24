# Roblox Moderation System

## Overview

This is a Discord bot integrated with a Flask API server designed for moderating Roblox game servers. The system allows Discord users with specific roles to execute moderation commands (like banning players, blacklisting assets) that are then consumed by Roblox game servers via the Flask API.

The architecture follows a command-queue pattern where Discord commands are stored on the Flask server and polled by Roblox game servers.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

1. **Discord Bot (`bot.py`)**
   - Built with discord.py library using slash commands (`app_commands`)
   - Role-based access control with `ALLOWED_ROLE_ID` and `ADMIN_ROLE_ID`
   - Communicates with Flask API to queue moderation commands
   - Manages asset blacklisting through API calls
   - Generates ban list exports in JSON and TXT formats (stored in `banlists/` directory)

2. **Flask API Server (`server.py`)**
   - Lightweight REST API running on port 5000
   - In-memory storage for commands, banned users, and blacklisted assets
   - Endpoints for:
     - Command queuing (`/send_command`, `/get_commands`, `/clear_commands`)
     - Player count updates (`/update_players`)
     - Blacklist management (referenced in bot.py but endpoints not fully shown)

3. **Application Entry Point (`main.py`)**
   - Runs Flask server in a background daemon thread
   - Runs Discord bot in the main thread
   - Environment validation for `DISCORD_TOKEN`

### Data Flow

1. Discord user issues a command via slash command
2. Bot validates user role permissions
3. Command is sent to Flask API via HTTP POST
4. Roblox game servers poll `/get_commands` endpoint
5. Commands are executed in-game and cleared via `/clear_commands`

### Configuration

- Environment variables loaded via `python-dotenv`
- Required secrets: `DISCORD_TOKEN`, `ALLOWED_ROLE_ID`, `ADMIN_ROLE_ID`
- External API URL configured for blacklist management

### Storage

- **In-memory**: Command queue, banned users set, blacklisted assets set (Flask server)
- **File-based**: Ban list exports stored in `banlists/` directory as JSON and TXT

## External Dependencies

### Third-Party Services

- **Discord API**: Bot authentication and slash command handling via discord.py
- **External Blacklist API**: Remote API at configured `API_URL` for persistent blacklist storage
- **Roblox Game Servers**: Expected to poll the Flask API for moderation commands

### Python Libraries

- `discord.py` (v2.6.4): Discord bot framework
- `Flask` (v3.1.2): REST API server
- `requests`: HTTP client for API communication
- `python-dotenv`: Environment variable management
- `pynacl`: Required for Discord voice support (optional feature)

### Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `DISCORD_TOKEN` | Discord bot authentication token |
| `ALLOWED_ROLE_ID` | Discord role ID for basic moderation access |
| `ADMIN_ROLE_ID` | Discord role ID for admin-level access |