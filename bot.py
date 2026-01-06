import os
import discord
import requests
import logging
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID", "0"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0"))
API_URL = "https://a0077eee-c497-43f3-b189-c4c77d39fa4e-00-24uu76dd8yyu8.riker.replit.dev/"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

class ModerationEmbed(discord.Embed):
    def __init__(self, title, description, color=discord.Color.blue()):
        super().__init__(title=title, description=description, color=color, timestamp=datetime.utcnow())

def is_authorized(interaction: discord.Interaction) -> bool:
    if ALLOWED_ROLE_ID == 0: 
        return True
    return any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles)

def is_admin(interaction: discord.Interaction) -> bool:
    if ADMIN_ROLE_ID == 0:
        return True
    return any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)

async def get_roblox_user_data(userid: str):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{userid}", timeout=5)
        if res.status_code != 200: 
            return None
        data = res.json()
        return {"name": data["name"], "display": data["displayName"]}
    except:
        return None

@bot.event
async def on_ready():
    await tree.sync()
    logger.info(f"Bot ready: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

# ===== LEVEL 1 COMMANDS =====

@tree.command(name="kick", description="Kick a player from the Roblox server")
async def kick_command(interaction: discord.Interaction, userid: str, reason: str = "Kicked by admin"):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/kick",
            json={
                "userid": userid,
                "reason": reason
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Kicked",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\n**Reason:** {reason}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Kick Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="mute", description="Mute a player from the Roblox server for a specified time")
async def mute_command(interaction: discord.Interaction, userid: str, duration: str, reason: str = "Muted by admin"):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/mute",
            json={
                "userid": userid,
                "duration": duration,
                "reason": reason
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Muted",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\n**Duration:** {duration}\n**Reason:** {reason}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Mute Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="umute", description="Removes the mute of a player from the Roblox server")
async def umute_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/umute",
            json={
                "userid": userid
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Unmuted",
                description=f"**Player:** {username}\n**UserID:** `{userid}`",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Unmute Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="userlogs", description="Displays a user's moderation logs")
async def userlogs_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        embed = ModerationEmbed(
            title="📋 User Logs",
            description=f"**Player:** {username}\n**UserID:** `{userid}`",
            color=discord.Color.blue()
        )

        try:
            response = requests.get(f"{API_URL}/user_logs?userid={userid}", timeout=10)
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    for log in logs[:5]:
                        embed.add_field(
                            name=f"{log.get('date', 'Unknown')} - {log.get('action', 'Action')}",
                            value=f"Reason: {log.get('reason', 'No reason')}\nBy: {log.get('moderator', 'Unknown')}",
                            inline=False
                        )
                else:
                    embed.add_field(name="No Logs", value="No moderation logs found.", inline=False)
            else:
                embed.add_field(name="API Error", value="Could not fetch logs.", inline=False)
        except:
            embed.add_field(name="Logs Unavailable", value="Logs API not accessible.", inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="addnote", description="Add a note to a player")
async def addnote_command(interaction: discord.Interaction, userid: str, note: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/add_note",
            json={
                "userid": userid,
                "note": note,
                "moderator": interaction.user.name
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Note Added",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\n**Note:** {note}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Failed to Add Note",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="userinfo", description="Display information about a user on Roblox")
async def userinfo_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        if not data:
            embed = ModerationEmbed(
                title="❌ User Not Found",
                description=f"UserID `{userid}` not found.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        embed = ModerationEmbed(
            title="👤 User Information",
            description=f"**Roblox Profile:** {data['name']}",
            color=discord.Color.blue()
        )

        embed.add_field(name="Username", value=data['name'], inline=True)
        embed.add_field(name="Display Name", value=data['display'], inline=True)
        embed.add_field(name="UserID", value=f"`{userid}`", inline=True)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="gameinfo", description="Display the info of a Roblox game")
async def gameinfo_command(interaction: discord.Interaction, placeid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.get(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={placeid}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                game = data[0]
                embed = ModerationEmbed(
                    title="🎮 Game Information",
                    description=f"**Game:** {game.get('name', 'Unknown')}",
                    color=discord.Color.purple()
                )

                embed.add_field(name="Place ID", value=f"`{placeid}`", inline=True)
                embed.add_field(name="Name", value=game.get('name', 'Unknown'), inline=True)
                embed.add_field(name="Description", value=game.get('description', 'No description')[:100] + "...", inline=False)
            else:
                embed = ModerationEmbed(
                    title="❌ Game Not Found",
                    description=f"Place ID `{placeid}` not found.",
                    color=discord.Color.red()
                )
        else:
            embed = ModerationEmbed(
                title="❌ Error",
                description=f"Failed to get game info: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

# ===== LEVEL 2 COMMANDS =====

@tree.command(name="ban", description="Ban a player from the Roblox server")
async def ban_command(interaction: discord.Interaction, userid: str, reason: str = "Banned by admin"):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/ban",
            json={
                "userid": userid,
                "reason": reason
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Banned",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\n**Reason:** {reason}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Ban Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="tempban", description="Temporarily ban a player from the Roblox server for a specified duration")
async def tempban_command(interaction: discord.Interaction, userid: str, duration: str, reason: str = "Temporarily banned"):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/tempban",
            json={
                "userid": userid,
                "duration": duration,
                "reason": reason
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Temp Banned",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\n**Duration:** {duration}\n**Reason:** {reason}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Temp Ban Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="unban", description="Remove the ban from a player on the Roblox server")
async def unban_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/unban",
            json={
                "userid": userid
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Unbanned",
                description=f"**Player:** {username}\n**UserID:** `{userid}`",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Unban Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="banasync", description="BanAsync a player by userid")
async def banasync_command(interaction: discord.Interaction, userid: str, reason: str = "Banned by admin"):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/BanAsync",
            json={
                "userid": userid,
                "reason": reason
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Banned (Async)",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\n**Reason:** {reason}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ BanAsync Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="unbanasync", description="unBanAsync a player by userid")
async def unbanasync_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/unBanAsync",
            json={
                "userid": userid
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Player Unbanned (Async)",
                description=f"**Player:** {username}\n**UserID:** `{userid}`",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ unBanAsync Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="banlist", description="Display a list of all banned players")
async def banlist_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.get(f"{API_URL}/get_bans", timeout=10)

        if response.status_code == 200:
            bans = response.json()
            if bans:
                embed = ModerationEmbed(
                    title="🔨 Ban List",
                    description=f"**Total bans:** {len(bans)}",
                    color=discord.Color.dark_red()
                )

                for i, ban in enumerate(bans[:10]):
                    userid = ban.get('userid', 'Unknown')
                    reason = ban.get('reason', 'No reason')
                    embed.add_field(
                        name=f"Player {i+1}",
                        value=f"ID: `{userid}`\nReason: {reason}",
                        inline=True
                    )

                if len(bans) > 10:
                    embed.set_footer(text=f"And {len(bans)-10} more bans...")
            else:
                embed = ModerationEmbed(
                    title="✅ No Bans",
                    description="No players are currently banned.",
                    color=discord.Color.green()
                )
        else:
            embed = ModerationEmbed(
                title="❌ Error",
                description=f"Failed to get ban list: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="admote", description="Add a note to a player (alias for addnote)")
async def admote_command(interaction: discord.Interaction, userid: str, note: str):
    await addnote_command.callback(interaction, userid, note)

# ===== LEVEL 3 COMMANDS =====

@tree.command(name="announcement", description="Display an announcement on the Roblox server")
async def announcement_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.post(
            f"{API_URL}/announce",
            json={
                "message": message
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="📢 Announcement Sent",
                description=f"**Message:** {message}",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Announcement Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="shutdown", description="Shutdown all Roblox servers")
async def shutdown_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.post(
            f"{API_URL}/shutdown",
            json={},
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="🛑 Server Shutdown",
                description="All Roblox servers have been shut down.",
                color=discord.Color.red()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Shutdown Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="cleanotes", description="Remove all moderation notes from a player")
async def cleanotes_command(interaction: discord.Interaction, userid: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/cleanotes",
            json={
                "userid": userid
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Notes Cleared",
                description=f"**Player:** {username}\n**UserID:** `{userid}`\nAll moderation notes have been removed.",
                color=discord.Color.green()
            )
        else:
            embed = ModerationEmbed(
                title="❌ Clear Failed",
                description=f"Error: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

# ===== UTILITY COMMANDS =====

@tree.command(name="players", description="Show online players list")
async def players_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.get(f"{API_URL}/get_players", timeout=10)

        if response.status_code == 200:
            data = response.json()
            players_list = data.get('players', [])
            player_count = data.get('count', 0)

            embed = ModerationEmbed(
                title="👥 Online Players",
                description=f"**Total online:** {player_count}",
                color=discord.Color.green()
            )

            if not players_list:
                if player_count > 0:
                    embed.description += "\n\n(Player details not yet synced from game)"
                else:
                    embed.description = "No players currently online."
            else:
                for i, p in enumerate(players_list[:10]):
                    username = p.get('username', 'Unknown')
                    userid = p.get('userid', 'Unknown')
                    playtime = p.get('playtime', 0)
                    
                    embed.add_field(
                        name=f"#{i+1} {username}",
                        value=f"ID: `{userid}`\nPlaytime: {playtime}m",
                        inline=True
                    )

            if player_count > 10:
                embed.set_footer(text=f"And {player_count-10} more players...")
        else:
            embed = ModerationEmbed(
                title="❌ Error",
                description=f"Failed to get player list: {response.status_code}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Cannot get player list: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@tree.command(name="help", description="Show all RoGuard commands")
async def help_command(interaction: discord.Interaction):
    embed = ModerationEmbed(
        title="🤖 RoGuard Commands",
        description="Game server moderation bot for Roblox",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="**Level 1 Commands**",
        value="""
`/kick` - Kick a player
`/mute` - Mute a player for time
`/umute` - Remove mute
`/userlogs` - View user logs
`/addnote` - Add note to player
`/userinfo` - Get user info
`/gameinfo` - Get game info""",
        inline=False
    )

    embed.add_field(
        name="**Level 2 Commands**",
        value="""
`/ban` - Ban a player
`/Tempban` - Temporary ban
`/unban` - Remove ban
`/BanAsync` - Async ban
`/unBanAsync` - Async unban
`/banlist` - View all bans
`/admote` - Add note (alias)""",
        inline=False
    )

    embed.add_field(
        name="**Level 3 Commands**",
        value="""
`/announcement` - Send announcement
`/shutdown` - Shutdown servers
`/Cleanotes` - Clear all notes""",
        inline=False
    )

    embed.add_field(
        name="**Utility Commands**",
        value="""
`/players` - Online players
`/help` - This help menu""",
        inline=False
    )

    embed.set_footer(text="RoGuard @ 2022 - 2025 - All rights reserved.")
    await interaction.response.send_message(embed=embed)

def run():
    if TOKEN:
        logger.info("Starting RoGuard bot...")
        bot.run(TOKEN)
    else:
        logger.error("No token found.")

if __name__ == "__main__":
    run()