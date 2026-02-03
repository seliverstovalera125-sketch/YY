import os
import discord
import requests
import logging
import asyncio
import json
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID", "0"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0"))
API_URL = "https://a0077eee-c497-43f3-b189-c4c77d39fa4e-00-24uu76dd8yyu8.riker.replit.dev/"

BANLIST_DIR = "banlists"
if not os.path.exists(BANLIST_DIR):
    os.makedirs(BANLIST_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


class AssetBlacklist:

    def is_blacklisted(self, asset_id):
        try:
            res = requests.get(f"{API_URL}/is_blacklisted/{asset_id}",
                               timeout=5)
            if res.status_code == 200:
                return res.json().get('blacklisted', False)
        except:
            pass
        return False

    def add_asset(self, asset_id):
        try:
            res = requests.post(f"{API_URL}/add_blacklist",
                                json={"asset_id": asset_id},
                                timeout=5)
            return res.status_code == 200
        except:
            return False

    def remove_asset(self, asset_id):
        try:
            res = requests.post(f"{API_URL}/remove_blacklist",
                                json={"asset_id": asset_id},
                                timeout=5)
            return res.status_code == 200
        except:
            return False

    def get_all_assets(self):
        try:
            res = requests.get(f"{API_URL}/get_blacklist", timeout=5)
            if res.status_code == 200:
                return res.json().get('assets', [])
        except:
            pass
        return []


asset_blacklist = AssetBlacklist()


class ModerationEmbed(discord.Embed):

    def __init__(self,
                 title,
                 description,
                 color=discord.Color.blue(),
                 target_user=None,
                 moderator=None):
        super().__init__(title=title,
                         description=description,
                         color=color,
                         timestamp=datetime.utcnow())
        if target_user:
            self.add_field(name="Target", value=target_user, inline=True)
        if moderator:
            self.set_footer(text=f"Moderator: {moderator}",
                            icon_url=moderator.display_avatar.url if hasattr(
                                moderator, 'display_avatar') else None)


class ConfirmActionView(View):

    def __init__(self,
                 action: str,
                 userid: str,
                 reason: str,
                 username: str,
                 interaction_user: discord.User | discord.Member,
                 duration: int = -1,
                 is_admin=False,
                 ban_type: str = "normal"):
        super().__init__(timeout=60)
        self.action = action
        self.userid = userid
        self.reason = reason
        self.username = username
        self.duration = duration
        self.interaction_user = interaction_user
        self.is_admin = is_admin
        self.ban_type = ban_type

    @discord.ui.button(label="Confirm",
                       style=discord.ButtonStyle.danger,
                       emoji="⚡")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                " This is not your session.", ephemeral=True)
            return

        button.disabled = True
        button.label = "Processing..."
        await interaction.response.edit_message(view=self)

        try:
            if self.action in ["restart", "shutdown"]:
                data = {
                    "command": self.action,
                    "executor": interaction.user.name
                }
            elif self.action == "ban":
                data = {
                    "command": self.action,
                    "userid": self.userid,
                    "reason": self.reason,
                    "duration": self.duration,
                    "executor": interaction.user.name,
                    "banType": self.ban_type
                }
            elif self.action == "pcban":
                data = {
                    "command": "pcban",
                    "userid": self.userid,
                    "reason": self.reason,
                    "executor": interaction.user.name,
                    "username": self.username
                }
            else:
                data = {
                    "command": self.action,
                    "userid": self.userid,
                    "reason": self.reason,
                    "executor": interaction.user.name
                }

            logger.info(f"Sending command to API: {data}")
            response = requests.post(f"{API_URL}/send_command",
                                     json=data,
                                     timeout=10)
            response.raise_for_status()
            logger.info(
                f"API Response: {response.status_code} - {response.text}")

            if self.action == "ban":
                if self.duration == -1:
                    duration_text = "permanently"
                else:
                    duration_text = f"for {self.duration} days"

                if self.ban_type == "pc":
                    ban_type_text = "PC "
                else:
                    ban_type_text = ""

                embed = ModerationEmbed(
                    title=f"✅ {ban_type_text}Ban Executed",
                    description=
                    f"**{self.username}** has been {ban_type_text}banned {duration_text}.",
                    color=discord.Color.green(),
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user)
                embed.add_field(name="Reason", value=self.reason, inline=False)
                if self.ban_type == "pc":
                    embed.add_field(name="Type",
                                    value="PC Ban (Device-based)",
                                    inline=True)
            elif self.action == "pcban":
                embed = ModerationEmbed(
                    title="✅ PC Ban Executed",
                    description=
                    f"**{self.username}** has been PC banned (permanent).",
                    color=discord.Color.red(),
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user)
                embed.add_field(name="Reason", value=self.reason, inline=False)
                embed.add_field(name="Type",
                                value="PC Ban (Device-based)",
                                inline=True)
                embed.add_field(name="Status", value="Permanent", inline=True)
            elif self.action == "kick":
                embed = ModerationEmbed(
                    title="✅ Kick Executed",
                    description=f"**{self.username}** has been kicked.",
                    color=discord.Color.green(),
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user)
                embed.add_field(name="Reason", value=self.reason, inline=False)
            elif self.action == "restart":
                embed = ModerationEmbed(
                    title="🔄 Server Restarting",
                    description="Server restart command sent.",
                    color=discord.Color.orange(),
                    moderator=interaction.user)
            elif self.action == "shutdown":
                embed = ModerationEmbed(
                    title="🛑 Server Shutdown",
                    description="Server shutdown command sent.",
                    color=discord.Color.red(),
                    moderator=interaction.user)
            elif self.action == "mute":
                embed = ModerationEmbed(
                    title="✅ Mute Executed",
                    description=f"**{self.username}** has been muted for {self.duration} minutes.",
                    color=discord.Color.orange(),
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user)
                embed.add_field(name="Reason", value=self.reason, inline=False)
            elif self.action == "umute":
                embed = ModerationEmbed(
                    title="✅ Unmute Executed",
                    description=f"**{self.username}** has been unmuted.",
                    color=discord.Color.green(),
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user)
            else:
                embed = ModerationEmbed(
                    title="✅ Action Completed",
                    description=f"Command executed: {self.action}",
                    color=discord.Color.green(),
                    moderator=interaction.user)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)
        except requests.exceptions.ConnectionError:
            await interaction.edit_original_response(
                content="Failed to connect to game server.", view=None)
        except requests.exceptions.Timeout:
            await interaction.edit_original_response(content="Server timeout.",
                                                     view=None)
        except Exception as e:
            await interaction.edit_original_response(
                content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "This is not your session.", ephemeral=True)
            return

        await interaction.response.edit_message(content="Action cancelled.",
                                                embed=None,
                                                view=None)


def save_banlist_to_disk(bans: list) -> str:
    """Save banlist to disk and return file path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"banlist_{timestamp}.json"
    filepath = os.path.join(BANLIST_DIR, filename)

    # Save in JSON format
    data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_bans": len(bans),
            "server": "Game Server",
            "version": "1.0"
        },
        "bans": bans
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Also save in text format for readability
    txt_filename = f"banlist_{timestamp}.txt"
    txt_filepath = os.path.join(BANLIST_DIR, txt_filename)

    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"SERVER BAN LIST\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total bans: {len(bans)}\n")
        f.write("=" * 70 + "\n\n")

        if not bans:
            f.write("No bans found.\n")
        else:
            for i, ban in enumerate(bans, 1):
                userid = ban.get('userid', 'Unknown')
                username = ban.get('username', 'Unknown')
                display_name = ban.get('display_name', username)
                reason = ban.get('reason', 'No reason')
                executor = ban.get('executor', 'Unknown')
                timestamp_ban = ban.get('timestamp', 0)
                duration = ban.get('duration', -1)
                ban_type = ban.get('banType', 'normal')

                if timestamp_ban and timestamp_ban != 'Unknown':
                    try:
                        date_str = datetime.fromtimestamp(
                            timestamp_ban).strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = str(timestamp_ban)
                else:
                    date_str = "N/A"

                duration_text = "Permanent" if duration == -1 else f"{duration} days"
                ban_type_text = "PC Ban" if ban_type == "pc" else "Normal Ban"

                # Format user display for file
                if display_name != username and display_name:
                    user_display = f"{username} (@{display_name})"
                else:
                    user_display = username

                f.write(f"#{i:3d} {ban_type_text.upper():10} {user_display}\n")
                f.write(f"     ID: {userid}\n")
                f.write(f"     Reason: {reason}\n")
                f.write(f"     Duration: {duration_text}\n")
                f.write(f"     Banned by: {executor}\n")
                f.write(f"     Date: {date_str}\n")
                f.write("-" * 50 + "\n")

    logger.info(f"Banlist saved: {filename} and {txt_filename}")
    return filepath


class BanListView(View):

    def __init__(self,
                 bans: list,
                 interaction_user: discord.User | discord.Member,
                 page: int = 1,
                 saved_filename: str = ""):
        super().__init__(timeout=120)
        self.bans = bans
        self.page = page
        self.items_per_page = 5
        self.total_pages = max(1, (len(bans) + self.items_per_page - 1) //
                               self.items_per_page)
        self.interaction_user = interaction_user
        self.saved_filename = saved_filename

        if self.page <= 1:
            for child in self.children:
                if isinstance(child, discord.ui.Button) and child.label == "◀ Previous":
                    child.disabled = True
        if self.page >= self.total_pages:
            for child in self.children:
                if isinstance(child, discord.ui.Button) and child.label == "Next ▶":
                    child.disabled = True

    def get_embed(self):
        start_idx = (self.page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.bans))

        embed = ModerationEmbed(
            title="🔨 Ban List",
            description=
            f"Total bans: {len(self.bans)}\nPage: {self.page}/{self.total_pages}",
            color=discord.Color.dark_red())

        if not self.bans:
            embed.description = "No bans found."
            embed.color = discord.Color.green()
            return embed

        for i in range(start_idx, end_idx):
            ban = self.bans[i]
            userid = ban.get('userid', 'Unknown')
            username = ban.get('username', 'Unknown')
            display_name = ban.get('display_name', username)
            reason = ban.get('reason', 'No reason')
            executor = ban.get('executor', 'Unknown')
            timestamp = ban.get('timestamp', 0)
            duration = ban.get('duration', -1)
            ban_type = ban.get('banType', 'normal')

            if duration == -1:
                duration_text = "Permanent"
            else:
                duration_text = f"{duration} days"

            if timestamp and timestamp != 'Unknown':
                try:
                    date_str = datetime.fromtimestamp(timestamp).strftime(
                        '%Y-%m-%d %H:%M')
                except:
                    date_str = str(timestamp)
            else:
                date_str = "N/A"

            ban_type_icon = "💻" if ban_type == "pc" else "🔨"
            ban_type_text = "PC Ban" if ban_type == "pc" else "Normal"

            if display_name != username and display_name:
                user_display = f"{username} (@{display_name})"
            else:
                user_display = username

            embed.add_field(
                name=f"#{i+1} {ban_type_icon} {user_display}",
                value=
                f"ID: `{userid}`\nReason: {reason}\nDuration: {duration_text}\nType: {ban_type_text}\nBy: {executor}\nDate: {date_str}",
                inline=False)

        # Add save information
        if self.saved_filename:
            embed.add_field(
                name="Auto-saved",
                value=f"Ban list automatically saved to server files.",
                inline=False)
            embed.set_footer(
                text=f"File: {os.path.basename(self.saved_filename)}")

        return embed

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction,
                            button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        if self.page > 1:
            self.page -= 1
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction,
                        button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        if self.page < self.total_pages:
            self.page += 1
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.primary)
    async def refresh_list(self, interaction: discord.Interaction,
                           button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.defer()

        try:
            response = requests.get(f"{API_URL}/get_bans", timeout=10)
            response.raise_for_status()
            bans = response.json()

            enriched_bans = []
            for ban in bans:
                userid = ban.get('userid', 'Unknown')
                username = ban.get('username', 'Unknown')

                if username in ["Unknown", "1"] and userid != "Unknown":
                    try:
                        roblox_data = await get_roblox_user_data(userid)
                        if roblox_data:
                            ban['username'] = roblox_data['name']
                            ban['display_name'] = roblox_data['display']
                        else:
                            ban['username'] = f"User {userid}"
                            ban['display_name'] = f"User {userid}"
                    except:
                        ban['username'] = f"User {userid}"
                        ban['display_name'] = f"User {userid}"
                else:
                    if 'display_name' not in ban:
                        if username != "Unknown" and userid != "Unknown":
                            try:
                                roblox_data = await get_roblox_user_data(userid
                                                                         )
                                if roblox_data:
                                    ban['display_name'] = roblox_data[
                                        'display']
                                else:
                                    ban['display_name'] = username
                            except:
                                ban['display_name'] = username
                        else:
                            ban['display_name'] = username

                enriched_bans.append(ban)

            saved_filepath = save_banlist_to_disk(enriched_bans)

            self.bans = enriched_bans
            self.total_pages = max(
                1, (len(enriched_bans) + self.items_per_page - 1) //
                self.items_per_page)
            self.page = min(self.page, self.total_pages)
            self.saved_filename = saved_filepath

            embed = self.get_embed()
            await interaction.edit_original_response(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Failed to refresh banlist: {str(e)}")
            await interaction.followup.send("Failed to refresh.",
                                            ephemeral=True)

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.danger)
    async def close_view(self, interaction: discord.Interaction,
                         button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.edit_message(content="Closed.",
                                                embed=None,
                                                view=None)


class UnbanView(View):

    def __init__(self,
                 userid: str,
                 username: str,
                 display_name: str,
                 interaction_user: discord.User | discord.Member,
                 ban_type: str = "normal"):
        super().__init__(timeout=60)
        self.userid = userid
        self.username = username
        self.interaction_user = interaction_user
        self.ban_type = ban_type

    @discord.ui.button(label="Confirm Unban",
                       style=discord.ButtonStyle.success,
                       emoji="✅")
    async def confirm_unban(self, interaction: discord.Interaction,
                            button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(" Not your session.",
                                                    ephemeral=True)
            return

        button.disabled = True
        button.label = "Processing..."
        await interaction.response.edit_message(view=self)

        try:
            if self.ban_type == "pc":
                data = {
                    "command": "unpcban",
                    "userid": self.userid,
                    "executor": interaction.user.name
                }
            else:
                data = {
                    "command": "unban",
                    "userid": self.userid,
                    "executor": interaction.user.name
                }

            logger.info(f"Sending unban command: {data}")
            response = requests.post(f"{API_URL}/send_command",
                                     json=data,
                                     timeout=10)
            response.raise_for_status()
            logger.info(
                f"Unban response: {response.status_code} - {response.text}")

            ban_type_text = "PC " if self.ban_type == "pc" else ""

            embed = ModerationEmbed(
                title=f"✅ {ban_type_text}Unbanned",
                description=
                f"**{self.username}** has been {ban_type_text}unbanned.",
                color=discord.Color.green(),
                target_user=f"{self.username} ({self.userid})",
                moderator=interaction.user)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except Exception as e:
            logger.error(f"Failed to unban: {str(e)}")
            await interaction.edit_original_response(
                content=f"Failed to unban: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.edit_message(content="Cancelled.",
                                                embed=None,
                                                view=None)


class PCBanView(View):

    def __init__(self, userid: str, reason: str, username: str,
                 display_name: str, interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.userid = userid
        self.reason = reason
        self.username = username
        self.display_name = display_name
        self.interaction_user = interaction_user

    @discord.ui.button(label="Confirm PC Ban",
                       style=discord.ButtonStyle.danger,
                       emoji="💻")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "This is not your session.", ephemeral=True)
            return

        button.disabled = True
        button.label = "Processing..."
        await interaction.response.edit_message(view=self)

        try:
            pcban_data = {
                "command": "pcban",
                "userid": self.userid,
                "reason": self.reason,
                "executor": interaction.user.name,
                "username": self.username
            }

            logger.info(f"Sending PC ban command: {pcban_data}")
            response = requests.post(f"{API_URL}/send_command",
                                     json=pcban_data,
                                     timeout=10)
            response.raise_for_status()
            logger.info(
                f"PC ban response: {response.status_code} - {response.text}")

            embed = ModerationEmbed(
                title="PC Ban Executed",
                description=f"**{self.username}** has been PC banned.",
                color=discord.Color.red(),
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user)
            embed.add_field(name="Reason", value=self.reason, inline=False)
            embed.add_field(name="Type",
                            value="PC Ban (Device-based)",
                            inline=True)
            embed.add_field(name="Status", value="Permanent", inline=True)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except requests.exceptions.ConnectionError:
            await interaction.edit_original_response(
                content="Failed to connect to game server.", view=None)
        except requests.exceptions.Timeout:
            await interaction.edit_original_response(content="Server timeout.",
                                                     view=None)
        except Exception as e:
            logger.error(f"PC ban error: {str(e)}")
            await interaction.edit_original_response(
                content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "This is not your session.", ephemeral=True)
            return

        await interaction.response.edit_message(content="PC Ban cancelled.",
                                                embed=None,
                                                view=None)


class UnPCBanView(View):

    def __init__(self, userid: str, username: str, display_name: str,
                 interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.userid = userid
        self.username = username
        self.display_name = display_name
        self.interaction_user = interaction_user

    @discord.ui.button(label="Confirm Unban",
                       style=discord.ButtonStyle.success,
                       emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "This is not your session.", ephemeral=True)
            return

        button.disabled = True
        button.label = "Processing..."
        await interaction.response.edit_message(view=self)

        try:
            unpcban_data = {
                "command": "unpcban",
                "userid": self.userid,
                "executor": interaction.user.name
            }

            logger.info(f"Sending PC unban command: {unpcban_data}")

            response = requests.post(f"{API_URL}/send_command",
                                     json=unpcban_data,
                                     timeout=10)
            response.raise_for_status()

            logger.info(
                f"PC unban response: {response.status_code} - {response.text}")

            embed = ModerationEmbed(
                title="PC Unban Executed",
                description=f"**{self.username}** has been PC unbanned.",
                color=discord.Color.green(),
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user)
            embed.add_field(name="Type",
                            value="PC Unban (Device-based)",
                            inline=True)
            embed.add_field(
                name="Note",
                value="The player can now join from previously banned devices.",
                inline=False)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except requests.exceptions.ConnectionError:
            await interaction.edit_original_response(
                content="Failed to connect to game server.", view=None)
        except requests.exceptions.Timeout:
            await interaction.edit_original_response(content="Server timeout.",
                                                     view=None)
        except Exception as e:
            logger.error(f"PC unban error: {str(e)}")
            await interaction.edit_original_response(
                content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "This is not your session.", ephemeral=True)
            return

        await interaction.response.edit_message(content="PC Unban cancelled.",
                                                embed=None,
                                                view=None)


class AnnounceView(View):

    def __init__(self, message: str, interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.message = message
        self.interaction_user = interaction_user

    @discord.ui.button(label="Send Announcement",
                       style=discord.ButtonStyle.primary,
                       emoji="📢")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        button.disabled = True
        button.label = "Sending..."
        await interaction.response.edit_message(view=self)

        try:
            announce_data = {
                "command": "announce",
                "message": self.message,
                "executor": interaction.user.name
            }
            response = requests.post(f"{API_URL}/send_command",
                                     json=announce_data,
                                     timeout=10)
            response.raise_for_status()

            embed = ModerationEmbed(
                title="Announcement Sent",
                description="Announcement has been sent to all players.",
                color=discord.Color.green(),
                moderator=interaction.user)
            embed.add_field(name="Message", value=self.message, inline=False)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except Exception as e:
            await interaction.edit_original_response(
                content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(" Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.edit_message(
            content="Announcement cancelled.", embed=None, view=None)


class BroadcastView(View):

    def __init__(self, message: str, interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.message = message
        self.interaction_user = interaction_user

    @discord.ui.button(label="Send Broadcast",
                       style=discord.ButtonStyle.primary,
                       emoji="📡")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        button.disabled = True
        button.label = "Sending..."
        await interaction.response.edit_message(view=self)

        try:
            broadcast_data = {
                "command": "broadcast",
                "message": self.message,
                "executor": interaction.user.name
            }
            response = requests.post(f"{API_URL}/send_command",
                                     json=broadcast_data,
                                     timeout=10)
            response.raise_for_status()

            embed = ModerationEmbed(
                title="Broadcast Sent",
                description="Message broadcasted to all players.",
                color=discord.Color.blue(),
                moderator=interaction.user)
            embed.add_field(name="Message", value=self.message, inline=False)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except Exception as e:
            await interaction.edit_original_response(
                content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.edit_message(content="Broadcast cancelled.",
                                                embed=None,
                                                view=None)


class NoteView(View):

    def __init__(self, userid: str, note: str, username: str,
                 display_name: str, interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.userid = userid
        self.note = note
        self.username = username
        self.display_name = display_name
        self.interaction_user = interaction_user

    @discord.ui.button(label="Confirm Note",
                       style=discord.ButtonStyle.primary,
                       emoji="📝")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        button.disabled = True
        button.label = "Adding..."
        await interaction.response.edit_message(view=self)

        try:
            note_data = {
                "command": "addnote",
                "userid": self.userid,
                "note": self.note,
                "executor": interaction.user.name
            }
            response = requests.post(f"{API_URL}/send_command",
                                     json=note_data,
                                     timeout=10)
            response.raise_for_status()

            embed = ModerationEmbed(
                title="Note Added",
                description=f"**{self.username}** has a new note.",
                color=discord.Color.green(),
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user)
            embed.add_field(name="Note", value=self.note, inline=False)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except Exception as e:
            await interaction.edit_original_response(
                content=f"❌ Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.edit_message(content="Note cancelled.",
                                                embed=None,
                                                view=None)


class CleanNotesView(View):

    def __init__(self, userid: str, username: str, display_name: str,
                 interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.userid = userid
        self.username = username
        self.display_name = display_name
        self.interaction_user = interaction_user

    @discord.ui.button(label="Confirm Clean Notes",
                       style=discord.ButtonStyle.danger,
                       emoji="🧹")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        button.disabled = True
        button.label = "Cleaning..."
        await interaction.response.edit_message(view=self)

        try:
            clean_data = {
                "command": "cleannotes",
                "userid": self.userid,
                "executor": interaction.user.name
            }
            response = requests.post(f"{API_URL}/send_command",
                                     json=clean_data,
                                     timeout=10)
            response.raise_for_status()

            embed = ModerationEmbed(
                title="Notes Cleaned",
                description=
                f"All notes for **{self.username}** have been removed.",
                color=discord.Color.green(),
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user)

            await interaction.edit_original_response(content=None,
                                                     embed=embed,
                                                     view=None)

        except Exception as e:
            await interaction.edit_original_response(
                content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session.",
                                                    ephemeral=True)
            return

        await interaction.response.edit_message(
            content="Clean notes cancelled.", embed=None, view=None)


def is_authorized(interaction: discord.Interaction) -> bool:
    if ALLOWED_ROLE_ID == 0:
        return True
    if not isinstance(interaction.user, discord.Member):
        return False
    return any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles)


def is_admin(interaction: discord.Interaction) -> bool:
    if ADMIN_ROLE_ID == 0:
        return True
    if not isinstance(interaction.user, discord.Member):
        return False
    return any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)


async def get_roblox_user_data(userid: str):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{userid}",
                           timeout=5)
        if res.status_code != 200:
            return None
        data = res.json()

        thumb_res = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png",
            timeout=5)
        avatar = None
        if thumb_res.status_code == 200:
            avatar = thumb_res.json()["data"][0]["imageUrl"]

        return {
            "name": data["name"],
            "display": data["displayName"],
            "avatar": avatar
        }
    except:
        return None


def check_api():
    try:
        response = requests.get(f"{API_URL}/get_players", timeout=5)
        return response.status_code == 200
    except:
        return False


# ===== KICK COMMANDS =====
@tree.command(name="kick", description="Kick a player from the Roblox server")
@app_commands.describe(userid="Roblox UserID", reason="Kick reason")
async def kick_command(interaction: discord.Interaction, userid: str,
                       reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    embed = ModerationEmbed(title="Confirm Kick",
                            description=f"Kick **{data['name']}**?",
                            color=discord.Color.orange(),
                            target_user=f"{data['name']} (@{data['display']})",
                            moderator=interaction.user)
    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)

    await interaction.followup.send(embed=embed,
                                    view=ConfirmActionView(
                                        "kick", userid, reason, data['name'],
                                        interaction.user))


# ===== USERLOGS COMMANDS =====
@tree.command(name="userlogs", description="Displays a user's moderation logs")
@app_commands.describe(userid="Roblox UserID")
async def userlogs_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    try:
        response = requests.get(f"{API_URL}/user_logs?userid={userid}",
                                timeout=10)

        embed = ModerationEmbed(
            title="User Logs",
            description=f"Moderation history for **{data['name']}**",
            color=discord.Color.blue(),
            target_user=f"{data['name']} (@{data['display']})",
            moderator=interaction.user)

        if data['avatar']:
            embed.set_thumbnail(url=data['avatar'])

        embed.add_field(name="UserID", value=f"`{userid}`", inline=True)

        if response.status_code == 200:
            logs = response.json()
            if logs and len(logs) > 0:
                for i, log in enumerate(logs[:5]):
                    embed.add_field(
                        name=
                        f"{log.get('action', 'Action').title()} - {log.get('date', 'Unknown')}",
                        value=
                        f"**Reason:** {log.get('reason', 'No reason')}\n**Moderator:** {log.get('moderator', 'Unknown')}",
                        inline=False)
                if len(logs) > 5:
                    embed.set_footer(text=f"And {len(logs)-5} more logs...")
            else:
                embed.add_field(
                    name="No Logs",
                    value="No moderation logs found for this user.",
                    inline=False)
        else:
            embed.add_field(name="Logs Unavailable",
                            value="Could not fetch logs from server.",
                            inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(title="Error",
                                description=f"Cannot get user logs: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== ADDNOTE COMMANDS =====
@tree.command(name="addnote", description="Add a note to a player")
@app_commands.describe(userid="Roblox UserID", note="Note to add")
async def addnote_command(interaction: discord.Interaction, userid: str,
                          note: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    embed = ModerationEmbed(title="Confirm Note",
                            description=f"Add note to **{data['name']}**?",
                            color=discord.Color.blue(),
                            target_user=f"{data['name']} (@{data['display']})",
                            moderator=interaction.user)
    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="Note", value=note, inline=False)

    await interaction.followup.send(embed=embed,
                                    view=NoteView(userid, note, data['name'],
                                                  data['display'],
                                                  interaction.user))


# ===== USERINFO COMMANDS =====
@tree.command(name="userinfo",
              description="Display information about a user on Roblox")
@app_commands.describe(userid="Roblox UserID")
async def userinfo_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title=" Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    # Check ban status
    is_banned = False
    ban_reason = ""
    ban_type = "normal"

    try:
        bans_res = requests.get(f"{API_URL}/get_bans", timeout=5)
        if bans_res.status_code == 200:
            bans = bans_res.json()
            for ban in bans:
                if str(ban.get('userid')) == userid:
                    is_banned = True
                    ban_reason = ban.get('reason', 'No reason')
                    ban_type = ban.get('banType', 'normal')
                    break
    except:
        pass

    embed = ModerationEmbed(title="User Information",
                            description=f"Roblox profile information",
                            color=discord.Color.blue())

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="Username", value=data['name'], inline=True)
    embed.add_field(name="Display Name", value=data['display'], inline=True)
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)

    if is_banned:
        ban_status = "Banned"
        if ban_type == "pc":
            ban_status = "💻 PC Banned"
        embed.add_field(name="Ban Status", value=ban_status, inline=True)
        embed.add_field(name="Ban Reason", value=ban_reason, inline=False)
        embed.add_field(name="Ban Type",
                        value="PC Ban" if ban_type == "pc" else "Normal Ban",
                        inline=True)
    else:
        embed.add_field(name="Ban Status", value="Not banned", inline=True)

    await interaction.followup.send(embed=embed)


# ===== GAMEINFO COMMANDS =====
@tree.command(name="gameinfo", description="Display the info of a Roblox game")
@app_commands.describe(placeid="Roblox Place ID")
async def gameinfo_command(interaction: discord.Interaction, placeid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not placeid.isdigit():
        embed = ModerationEmbed(title="Invalid Place ID",
                                description="Place ID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    try:
        response = requests.get(
            f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={placeid}",
            timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                game = data[0]
                embed = ModerationEmbed(
                    title="🎮 Game Information",
                    description=f"**{game.get('name', 'Unknown Game')}**",
                    color=discord.Color.purple())

                embed.add_field(name="Place ID",
                                value=f"`{placeid}`",
                                inline=True)
                embed.add_field(name="Name",
                                value=game.get('name', 'Unknown'),
                                inline=True)
                embed.add_field(
                    name="Description",
                    value=game.get('description', 'No description')[:100] +
                    "...",
                    inline=False)

                # Try to get player count
                try:
                    players_res = requests.get(f"{API_URL}/get_players",
                                               timeout=5)
                    if players_res.status_code == 200:
                        players_data = players_res.json()
                        player_count = players_data.get('count', 0)
                        embed.add_field(name="Current Players",
                                        value=str(player_count),
                                        inline=True)
                except:
                    pass
            else:
                embed = ModerationEmbed(
                    title="Game Not Found",
                    description=f"Place ID `{placeid}` not found on Roblox.",
                    color=discord.Color.red())
        else:
            embed = ModerationEmbed(
                title="Error",
                description=f"Failed to get game info: {response.status_code}",
                color=discord.Color.red())

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(title="Error",
                                description=f"Cannot get game info: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== ANNOUNCMENT COMMANDS =====
@tree.command(name="announcement",
              description="Display an announcement on the Roblox server")
@app_commands.describe(message="Announcement message")
async def announcement_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    embed = ModerationEmbed(
        title="Announcement Confirmation",
        description=f"Send this announcement to all players?",
        color=discord.Color.gold(),
        moderator=interaction.user)
    embed.add_field(name="Message", value=message, inline=False)

    await interaction.response.send_message(embed=embed,
                                            view=AnnounceView(
                                                message, interaction.user))


# ===== CLEANOTES COMMANDS =====
@tree.command(name="cleanotes",
              description="Remove all moderation notes from a player")
@app_commands.describe(userid="Roblox UserID")
async def cleanotes_command(interaction: discord.Interaction, userid: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    embed = ModerationEmbed(
        title="Confirm Clean Notes",
        description=f"Remove ALL notes for **{data['name']}**?",
        color=discord.Color.orange(),
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user)
    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)
    embed.add_field(
        name="Warning",
        value=
        "This action cannot be undone! All notes will be permanently deleted.",
        inline=False)

    await interaction.followup.send(embed=embed,
                                    view=CleanNotesView(
                                        userid, data['name'], data['display'],
                                        interaction.user))


# ===== PING COMMANDS =====
@tree.command(name="ping", description="Check bot status")
async def ping_command(interaction: discord.Interaction):
    latency = round(bot.latency * 1000, 2)
    api_status = check_api()

    embed = ModerationEmbed(title="Kynx SS 10 Status",
                            description="Bot status check",
                            color=discord.Color.blue())

    embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=True)
    embed.add_field(name="API Status",
                    value="✅ Online" if api_status else "❌ Offline",
                    inline=True)
    embed.add_field(name="Version", value="SS 10", inline=True)

    await interaction.response.send_message(embed=embed)


# ===== BAN COMMANDS =====
@tree.command(name="ban", description="Ban a player")
@app_commands.describe(
    userid="Roblox UserID",
    reason="Ban reason",
    duration="Ban duration in days (default: -1 for permanent)",
    ban_type="Ban type: normal or pc")
async def ban_command(interaction: discord.Interaction,
                      userid: str,
                      reason: str,
                      duration: int = -1,
                      ban_type: str = "normal"):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    if duration == -1:
        duration_text = "permanent"
    else:
        duration_text = f"{duration} days"

    if ban_type not in ["normal", "pc"]:
        ban_type = "normal"

    ban_type_display = "PC Ban" if ban_type == "pc" else "Normal Ban"

    embed = ModerationEmbed(
        title=f"Confirm {ban_type_display}",
        description=f"{ban_type_display} **{data['name']}**?",
        color=discord.Color.dark_red()
        if ban_type == "pc" else discord.Color.orange(),
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user)
    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.add_field(name="Duration", value=duration_text, inline=True)
    embed.add_field(name="Type", value=ban_type_display, inline=True)

    await interaction.followup.send(embed=embed,
                                    view=ConfirmActionView("ban",
                                                           userid,
                                                           reason,
                                                           data['name'],
                                                           interaction.user,
                                                           duration,
                                                           ban_type=ban_type))


# ===== CHECK COMMANDS =====
@tree.command(name="check", description="Check server status")
async def check_command(interaction: discord.Interaction):
    try:
        res = requests.get(f"{API_URL}/get_players", timeout=5)
        res.raise_for_status()
        data = res.json()
        count = data.get('count', 0)

        if count == 0:
            embed = ModerationEmbed(title="🌙 Server Empty",
                                    description="No players online.",
                                    color=discord.Color.light_grey())
        elif count < 10:
            embed = ModerationEmbed(
                title="🟢 Server Online",
                description=
                f"{count} player{'s' if count != 1 else ''} online.",
                color=discord.Color.green())
        elif count < 30:
            embed = ModerationEmbed(title="🟡 Server Busy",
                                    description=f"{count} players online.",
                                    color=discord.Color.gold())
        else:
            embed = ModerationEmbed(title="🔴 Server Full",
                                    description=f"{count} players online.",
                                    color=discord.Color.red())

        await interaction.response.send_message(embed=embed)
    except:
        embed = ModerationEmbed(title="Server Error",
                                description="Cannot connect to server.",
                                color=discord.Color.red())
        await interaction.response.send_message(embed=embed)


# ===== BANLIST COMMANDS =====
@tree.command(name="banlist",
              description="View bans (automatically saves to server files)")
async def banlist_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.get(f"{API_URL}/get_bans", timeout=10)
        response.raise_for_status()
        bans = response.json()

        enriched_bans = []
        for ban in bans:
            userid = ban.get('userid', 'Unknown')
            username = ban.get('username', 'Unknown')

            if username in ["Unknown", "1"] and userid != "Unknown":
                try:
                    roblox_data = await get_roblox_user_data(userid)
                    if roblox_data:
                        ban['username'] = roblox_data['name']
                        ban['display_name'] = roblox_data['display']
                    else:
                        ban['username'] = f"User {userid}"
                        ban['display_name'] = f"User {userid}"
                except:
                    ban['username'] = f"User {userid}"
                    ban['display_name'] = f"User {userid}"
            else:
                if 'display_name' not in ban:
                    if username != "Unknown" and userid != "Unknown":
                        try:
                            roblox_data = await get_roblox_user_data(userid)
                            if roblox_data:
                                ban['display_name'] = roblox_data['display']
                            else:
                                ban['display_name'] = username
                        except:
                            ban['display_name'] = username
                    else:
                        ban['display_name'] = username

            enriched_bans.append(ban)

        saved_filepath = save_banlist_to_disk(enriched_bans)

        view = BanListView(enriched_bans,
                           interaction.user,
                           saved_filename=saved_filepath)
        embed = view.get_embed()

        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        logger.error(f"Error getting/saving banlist: {str(e)}")
        embed = ModerationEmbed(title="Connection Error",
                                description="Cannot get ban list.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== UNBAN COMMANDS =====
@tree.command(name="unban", description="Unban a player")
@app_commands.describe(
    userid="Roblox UserID to unban",
    ban_type="Ban type to unban: normal or pc (default: auto-detect)")
async def unban_command(interaction: discord.Interaction,
                        userid: str,
                        ban_type: str = "auto"):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    try:
        response = requests.get(f"{API_URL}/get_bans", timeout=10)
        response.raise_for_status()
        bans = response.json()

        user_ban = None
        for ban in bans:
            if str(ban.get('userid')) == userid:
                user_ban = ban
                break

        if not user_ban:
            embed = ModerationEmbed(
                title="Not banned",
                description=f"UserID `{userid}` is not banned.",
                color=discord.Color.orange())
            await interaction.followup.send(embed=embed)
            return

        roblox_data = await get_roblox_user_data(userid)
        username = roblox_data['name'] if roblox_data else user_ban.get(
            'username', 'Unknown')

        detected_ban_type = user_ban.get('banType', 'normal')
        if ban_type != "auto":
            detected_ban_type = ban_type

        embed = ModerationEmbed(
            title=f"Confirm {'PC ' if detected_ban_type == 'pc' else ''}Unban",
            description=
            f"{'PC ' if detected_ban_type == 'pc' else ''}Unban **{username}**?",
            color=discord.Color.gold(),
            target_user=f"{username} ({userid})",
            moderator=interaction.user)
        embed.add_field(name="Ban Reason",
                        value=user_ban.get('reason', 'No reason'),
                        inline=False)
        embed.add_field(name="Banned By",
                        value=user_ban.get('executor', 'Unknown'),
                        inline=True)
        embed.add_field(
            name="Ban Type",
            value="PC Ban" if detected_ban_type == "pc" else "Normal Ban",
            inline=True)

        if roblox_data and roblox_data['avatar']:
            embed.set_thumbnail(url=roblox_data['avatar'])

        view = UnbanView(userid, username, "", interaction.user, detected_ban_type)
        await interaction.followup.send(embed=embed, view=view)

    except:
        embed = ModerationEmbed(title="Error",
                                description="Cannot process unban.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== RESTART COMMANDS =====
@tree.command(name="restart", description="Restart server (Admin)")
async def restart_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    embed = ModerationEmbed(title="Restart Server",
                            description="Restart the game server?",
                            color=discord.Color.orange(),
                            moderator=interaction.user)
    embed.add_field(name="Warning",
                    value="All players will be disconnected.",
                    inline=False)

    view = ConfirmActionView("restart",
                             "",
                             "",
                             "",
                             interaction.user,
                             is_admin=True)
    await interaction.response.send_message(embed=embed, view=view)


# ===== SHUTDOWN COMMANDS =====
@tree.command(name="shutdown", description="Shutdown server (Admin)")
async def shutdown_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    embed = ModerationEmbed(title="Shutdown Server",
                            description="Shutdown the game server?",
                            color=discord.Color.red(),
                            moderator=interaction.user)
    embed.add_field(name="Warning",
                    value="Server will stop completely.",
                    inline=False)

    view = ConfirmActionView("shutdown",
                             "",
                             "",
                             "",
                             interaction.user,
                             is_admin=True)
    await interaction.response.send_message(embed=embed, view=view)


# ===== PLAYERS COMMANDS =====
@tree.command(name="players", description="Show detailed online player list")
async def players_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    try:
        players = []

        endpoints_to_try = [
            f"{API_URL}/players",
            f"{API_URL}/players/list",
            f"{API_URL}/get_players_detailed",
            f"{API_URL}/get_players",
        ]

        for endpoint in endpoints_to_try:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(
                        f"{endpoint} returned: {type(data)} - {str(data)[:100]}"
                    )

                    if isinstance(data, list):
                        players = data
                        break
                    elif isinstance(data, dict):
                        players_key = next((key for key in [
                            'players', 'Players', 'playerlist', 'PlayerList',
                            'data', 'Data'
                        ] if key in data), None)
                        if players_key:
                            players = data[players_key]
                            break
                        elif 'count' in data or 'online' in data:
                            player_count = data.get('count',
                                                    data.get('online', 0))
                            players = [{
                                "username": f"Player {i+1}",
                                "userid": "Unknown",
                                "playtime": "0m"
                            } for i in range(player_count)]
                            break
            except:
                continue

        embed = ModerationEmbed(
            title="Online Players",
            description=f"**Total online:** {len(players)}",
            color=discord.Color.green())

        if players and len(players) > 0:
            for i, player in enumerate(players[:10]):
                if isinstance(player,
                              dict) and 'username' in player and player[
                                  'username'].startswith('Player '):
                    embed.add_field(
                        name=player['username'],
                        value=
                        f"ID: `{player.get('userid', 'Unknown')}`\nPlaytime: {player.get('playtime', '0m')}",
                        inline=True)
                else:
                    username = "Unknown Player"
                    userid = "Unknown"
                    playtime = "0m"

                    if isinstance(player, dict):
                        username = player.get(
                            'name',
                            player.get('username',
                                       player.get('Name', f'Player {i+1}')))
                        userid = player.get(
                            'id',
                            player.get(
                                'userid',
                                player.get('steamId',
                                           player.get('steamid', 'Unknown'))))
                        playtime = player.get(
                            'playtime',
                            player.get('time', player.get('duration', '0m')))
                    elif isinstance(player, str):
                        username = player

                    embed.add_field(
                        name=username,
                        value=f"ID: `{userid}`\nPlaytime: {playtime}",
                        inline=True)

            if len(players) > 10:
                embed.set_footer(text=f"And {len(players)-10} more players...")
        else:
            embed.description = "**No players online.**"
            embed.color = discord.Color.light_grey()

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(
            title="Error",
            description=f"Cannot get player list: {str(e)}",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== WARN COMMANDS =====
@tree.command(name="warn", description="Warn a player")
async def warn_command(interaction: discord.Interaction, userid: str,
                       reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    class WarnView(View):

        def __init__(self, userid: str, reason: str, username: str,
                     interaction_user: discord.User | discord.Member):
            super().__init__(timeout=60)
            self.userid = userid
            self.reason = reason
            self.username = username
            self.interaction_user = interaction_user

        @discord.ui.button(label="Confirm Warn",
                           style=discord.ButtonStyle.secondary,
                           emoji="⚠️")
        async def confirm(self, interaction: discord.Interaction,
                          button: Button):
            if interaction.user != self.interaction_user:
                await interaction.response.send_message("Not your session.",
                                                        ephemeral=True)
                return

            button.disabled = True
            button.label = "Processing..."
            await interaction.response.edit_message(view=self)

            try:
                warning_data = {
                    "command": "warn",
                    "userid": self.userid,
                    "reason": self.reason,
                    "executor": interaction.user.name
                }
                response = requests.post(f"{API_URL}/send_command",
                                         json=warning_data,
                                         timeout=10)
                response.raise_for_status()

                embed = ModerationEmbed(
                    title="Player Warned",
                    description=f"**{self.username}** has been warned.",
                    color=discord.Color.orange(),
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user)
                embed.add_field(name="Reason", value=self.reason, inline=False)

                await interaction.edit_original_response(content=None,
                                                         embed=embed,
                                                         view=None)

            except Exception as e:
                await interaction.edit_original_response(
                    content=f"Error: {str(e)}", view=None)

        @discord.ui.button(label="Cancel",
                           style=discord.ButtonStyle.secondary,
                           emoji="✖️")
        async def cancel(self, interaction: discord.Interaction,
                         button: Button):
            if interaction.user != self.interaction_user:
                await interaction.response.send_message("Not your session.",
                                                        ephemeral=True)
                return

            await interaction.response.edit_message(content="Warn cancelled.",
                                                    embed=None,
                                                    view=None)

    embed = ModerationEmbed(title="Confirm Warning",
                            description=f"Warn **{data['name']}**?",
                            color=discord.Color.gold(),
                            target_user=f"{data['name']} (@{data['display']})",
                            moderator=interaction.user)
    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    await interaction.followup.send(embed=embed,
                                    view=WarnView(userid, reason, data['name'],
                                                  interaction.user))


# ===== STATS COMMANDS =====
@tree.command(name="stats", description="Server statistics")
async def stats_command(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        players_res = requests.get(f"{API_URL}/get_players", timeout=5)
        player_count = 0
        if players_res.status_code == 200:
            player_count = players_res.json().get('count', 0)

        bans_res = requests.get(f"{API_URL}/get_bans", timeout=5)
        ban_count = 0
        normal_bans = 0
        pc_bans = 0

        if bans_res.status_code == 200:
            bans = bans_res.json()
            ban_count = len(bans)

            for ban in bans:
                ban_type = ban.get('banType', 'normal')
                if ban_type == 'pc':
                    pc_bans += 1
                else:
                    normal_bans += 1

        embed = ModerationEmbed(title="Server Statistics",
                                description="Kynx SS 10 - Current server statistics",
                                color=discord.Color.purple())

        embed.add_field(name="Online Players",
                        value=str(player_count),
                        inline=True)
        embed.add_field(name="Total Bans", value=str(ban_count), inline=True)
        embed.add_field(name="Normal Bans",
                        value=str(normal_bans),
                        inline=True)
        embed.add_field(name="PC Bans", value=str(pc_bans), inline=True)
        embed.add_field(name="API Status", value="✅ Online", inline=True)
        embed.add_field(name="Version", value="SS 10", inline=True)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(title="Error",
                                description=f"Cannot get statistics: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== ANNOUNCE COMMANDS =====
@tree.command(name="announce", description="Send announcement to server")
@app_commands.describe(message="Announcement message")
async def announce_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    embed = ModerationEmbed(
        title="Announcement Confirmation",
        description=f"Send this announcement to all players?",
        color=discord.Color.gold(),
        moderator=interaction.user)
    embed.add_field(name="Message", value=message, inline=False)

    await interaction.response.send_message(embed=embed,
                                            view=AnnounceView(
                                                message, interaction.user))


# ===== BROADCAST COMMANDS =====
@tree.command(name="broadcast", description="Broadcast message to all players")
@app_commands.describe(message="Broadcast message")
async def broadcast_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    embed = ModerationEmbed(title="Broadcast Confirmation",
                            description=f"Send this broadcast to all players?",
                            color=discord.Color.blue(),
                            moderator=interaction.user)
    embed.add_field(name="Message", value=message, inline=False)

    await interaction.response.send_message(embed=embed,
                                            view=BroadcastView(
                                                message, interaction.user))


# ===== FIND COMMANDS =====
@tree.command(name="find", description="Find player by username")
@app_commands.describe(username="Username to search for")
async def find_command(interaction: discord.Interaction, username: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.get(f"{API_URL}/get_players", timeout=10)
        if response.status_code == 200:
            players_data = response.json()
            player_count = players_data.get('count', 0)

            embed = ModerationEmbed(title="Player Search",
                                    description=f"Searching for '{username}'",
                                    color=discord.Color.blue())

            if player_count > 0:
                embed.add_field(
                    name="Information",
                    value=
                    f"Found {player_count} player(s) online.\nNote: Detailed search requires player list API.",
                    inline=False)
            else:
                embed.add_field(name="No Players",
                                value="No players online to search.",
                                inline=False)

            await interaction.followup.send(embed=embed)
        else:
            embed = ModerationEmbed(title="Error",
                                    description="Cannot search for players.",
                                    color=discord.Color.red())
            await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(title="Error",
                                description=f"Search failed: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== LOOKUP COMMANDS =====
@tree.command(name="lookup", description="Check player moderation history")
@app_commands.describe(userid="Roblox UserID")
async def lookup_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"ID: {userid}"

    try:
        bans_res = requests.get(f"{API_URL}/get_bans", timeout=10)
        is_banned = False
        ban_reason = ""
        ban_type = "normal"

        if bans_res.status_code == 200:
            bans = bans_res.json()
            for ban in bans:
                if str(ban.get('userid')) == userid:
                    is_banned = True
                    ban_reason = ban.get('reason', 'No reason')
                    ban_type = ban.get('banType', 'normal')
                    break

        embed = ModerationEmbed(title="Player Lookup",
                                description=f"Information for **{username}**",
                                color=discord.Color.blue())

        if data:
            if data['avatar']:
                embed.set_thumbnail(url=data['avatar'])
            embed.add_field(name="Roblox Username",
                            value=data['name'],
                            inline=True)
            embed.add_field(name="Display Name",
                            value=data['display'],
                            inline=True)

        embed.add_field(name="UserID", value=f"`{userid}`", inline=True)

        if is_banned:
            ban_status = "Banned"
            if ban_type == "pc":
                ban_status = "PC Banned"
            embed.add_field(name="Ban Status", value=ban_status, inline=True)
            embed.add_field(name="Ban Reason", value=ban_reason, inline=False)
            embed.add_field(
                name="Ban Type",
                value="PC Ban" if ban_type == "pc" else "Normal Ban",
                inline=True)
        else:
            embed.add_field(name="Ban Status",
                            value="✅ Not banned",
                            inline=True)

        embed.add_field(
            name="Additional Info",
            value="More detailed history requires player history API.",
            inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(title="Error",
                                description=f"Cannot lookup player: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== LOGS COMMANDS =====
@tree.command(name="logs", description="View server logs")
@app_commands.describe(lines="Number of log lines (default: 10)")
async def logs_command(interaction: discord.Interaction, lines: int = 10):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        logs_res = requests.get(f"{API_URL}/get_logs?lines={lines}",
                                timeout=10)

        embed = ModerationEmbed(title="Server Logs",
                                description=f"Recent server activity",
                                color=discord.Color.dark_grey())

        if logs_res.status_code == 200:
            logs_data = logs_res.json()
            logs = logs_data.get('logs', [])

            if logs:
                log_text = ""
                for i, log in enumerate(logs[:lines], 1):
                    log_text += f"{i:2d}. {log}\n"

                if len(log_text) > 1000:
                    log_text = log_text[:997] + "..."

                embed.add_field(name=f"Last {len(logs)} entries:",
                                value=f"```\n{log_text}\n```",
                                inline=False)
            else:
                embed.add_field(name="No logs",
                                value="No log entries available.",
                                inline=False)
        else:
            embed.add_field(
                name="Logs unavailable",
                value=
                "Log API endpoint not available.\nCheck API server configuration.",
                inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ModerationEmbed(title="Error",
                                description=f"Cannot get logs: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== PCBAN COMMANDS =====
@tree.command(name="pcban", description="PC Ban player (Device-based ban)")
@app_commands.describe(userid="Roblox UserID", reason="Ban reason")
async def pcban_command(interaction: discord.Interaction, userid: str,
                        reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ModerationEmbed(
            title="User not found",
            description=f"ID `{userid}` not found on Roblox.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    # Check if user is already banned
    try:
        response = requests.get(f"{API_URL}/get_bans", timeout=10)
        if response.status_code == 200:
            bans = response.json()
            for ban in bans:
                if str(ban.get('userid')) == userid:
                    embed = ModerationEmbed(
                        title="Already Banned",
                        description=f"**{data['name']}** is already banned.",
                        color=discord.Color.orange(),
                        target_user=f"{data['name']} (@{data['display']})",
                        moderator=interaction.user)
                    embed.add_field(name="Current Ban Reason",
                                    value=ban.get('reason', 'No reason'),
                                    inline=False)
                    embed.add_field(name="Banned By",
                                    value=ban.get('executor', 'Unknown'),
                                    inline=True)
                    embed.add_field(name="Ban Type",
                                    value="PC Ban" if ban.get('banType')
                                    == 'pc' else 'Normal Ban',
                                    inline=True)
                    await interaction.followup.send(embed=embed)
                    return
    except:
        pass

    embed = ModerationEmbed(title="Confirm PC Ban",
                            description=f"PC Ban **{data['name']}**?",
                            color=discord.Color.dark_red(),
                            target_user=f"{data['name']} (@{data['display']})",
                            moderator=interaction.user)
    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])
    embed.add_field(name="UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.add_field(name="Ban Type",
                    value="PC Ban (Device-based)",
                    inline=True)

    embed.add_field(
        name="Warning",
        value=
        "PC bans are device-based and permanent. Player cannot join from the banned device even with different accounts.",
        inline=False)

    await interaction.followup.send(embed=embed,
                                    view=PCBanView(userid, reason,
                                                   data['name'],
                                                   data['display'],
                                                   interaction.user))


# ===== UNPCBAN COMMANDS =====
@tree.command(name="unpcban", description="Remove PC ban")
@app_commands.describe(userid="Roblox UserID to unban")
async def unpcban_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"
    display_name = data['display'] if data else username

    embed = ModerationEmbed(title="Confirm PC Unban",
                            description=f"PC Unban **{username}**?",
                            color=discord.Color.gold(),
                            target_user=f"{username} ({userid})",
                            moderator=interaction.user)

    if data and data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(
        name="Warning",
        value="This will remove the device-based PC ban for this user.",
        inline=False)

    await interaction.followup.send(embed=embed,
                                    view=UnPCBanView(userid, username,
                                                     display_name,
                                                     interaction.user))


# ===== BANASYNC COMMANDS =====
@tree.command(name="banasync", description="Ban a player by userid")
@app_commands.describe(userid="The Roblox user ID to ban",
                       reason="Reason for the ban")
async def banasync_command(interaction: discord.Interaction, userid: str,
                           reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"
        display_name = data['display'] if data else username

        # Send ban command WITHOUT duration field
        response = requests.post(
            f"{API_URL}/send_command",
            json={
                "command": "ban",
                "userid": userid,
                "reason": reason,
                "executor": interaction.user.name,
                "username": username,
                "banType": "normal"  # Or "pc" if needed
            },
            timeout=10)

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Ban Command Sent",
                description=f"**{username}** has been banned.",
                color=discord.Color.green(),
                target_user=f"{username} ({userid})",
                moderator=interaction.user)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Type", value="Normal Ban", inline=True)
        else:
            error_msg = response.text if response.text else f"Status: {response.status_code}"
            embed = ModerationEmbed(title="❌ Ban Command Failed",
                                    description=f"Error: {error_msg}",
                                    color=discord.Color.red())

        await interaction.followup.send(embed=embed)

    except requests.exceptions.Timeout:
        embed = ModerationEmbed(
            title="❌ Timeout Error",
            description="Request timed out. Server may be unavailable.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed to send ban command: {str(e)}",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== UNBANASYNC COMMANDS =====
@tree.command(name="unbanasync", description="Unban a player by userid")
@app_commands.describe(userid="The Roblox user ID to unban")
async def unbanasync_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        # Send unban command
        response = requests.post(f"{API_URL}/send_command",
                                 json={
                                     "command": "unban",
                                     "userid": userid,
                                     "executor": interaction.user.name
                                 },
                                 timeout=10)

        if response.status_code == 200:
            embed = ModerationEmbed(
                title="✅ Unban Command Sent",
                description=f"**{username}** has been unbanned.",
                color=discord.Color.green(),
                target_user=f"{username} ({userid})",
                moderator=interaction.user)
        else:
            error_msg = response.text if response.text else f"Status: {response.status_code}"
            embed = ModerationEmbed(title="❌ Unban Command Failed",
                                    description=f"Error: {error_msg}",
                                    color=discord.Color.red())

        await interaction.followup.send(embed=embed)

    except requests.exceptions.Timeout:
        embed = ModerationEmbed(
            title="❌ Timeout Error",
            description="Request timed out. Server may be unavailable.",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)
    except Exception as e:
        embed = ModerationEmbed(
            title="❌ Error",
            description=f"Failed to send unban command: {str(e)}",
            color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== MUTE COMMANDS =====
@tree.command(name="mute", description="Mute a player")
@app_commands.describe(userid="Roblox UserID",
                       duration="Duration in minutes (e.g. 10, 60, 1440)",
                       reason="Reason for the mute")
async def mute_command(interaction: discord.Interaction, userid: str,
                       duration: int, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"

    embed = ModerationEmbed(title="Confirm Mute",
                            description=f"Mute **{username}**?",
                            color=discord.Color.orange(),
                            target_user=f"{username} ({userid})",
                            moderator=interaction.user)
    embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)

    await interaction.followup.send(embed=embed,
                                    view=ConfirmActionView("mute",
                                                           userid,
                                                           reason,
                                                           username,
                                                           interaction.user,
                                                           duration=duration))


# ===== UNMUTE COMMANDS =====
@tree.command(name="umute", description="Unmute a player")
@app_commands.describe(userid="Roblox UserID")
async def umute_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="UserID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"

    embed = ModerationEmbed(title="Confirm Unmute",
                            description=f"Unmute **{username}**?",
                            color=discord.Color.green(),
                            target_user=f"{username} ({userid})",
                            moderator=interaction.user)

    await interaction.followup.send(embed=embed,
                                    view=ConfirmActionView(
                                        "umute", userid, "Unmuted via Discord",
                                        username, interaction.user))


# ===== BLACKLIST COMMANDS =====
@tree.command(name="blacklist", description="Add asset to blacklist")
@app_commands.describe(asset_id="Asset ID to blacklist")
async def blacklist_command(interaction: discord.Interaction, asset_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not asset_id.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="Asset ID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    try:
        if asset_blacklist.is_blacklisted(asset_id):
            embed = ModerationEmbed(title="Already Blacklisted",
                                    description=f"Asset `{asset_id}` is already blacklisted.",
                                    color=discord.Color.orange())
        else:
            if asset_blacklist.add_asset(asset_id):
                embed = ModerationEmbed(title="✅ Asset Blacklisted",
                                        description=f"Asset `{asset_id}` has been added to blacklist.",
                                        color=discord.Color.green())
            else:
                embed = ModerationEmbed(title="❌ Failed",
                                        description=f"Failed to blacklist asset `{asset_id}`.",
                                        color=discord.Color.red())
    except Exception as e:
        embed = ModerationEmbed(title="❌ Error",
                                description=f"Error: {str(e)}",
                                color=discord.Color.red())

    await interaction.followup.send(embed=embed)


# ===== UNBLACKLIST COMMANDS =====
@tree.command(name="unblacklist", description="Remove asset from blacklist")
@app_commands.describe(asset_id="Asset ID to remove from blacklist")
async def unblacklist_command(interaction: discord.Interaction, asset_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not asset_id.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="Asset ID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    try:
        if not asset_blacklist.is_blacklisted(asset_id):
            embed = ModerationEmbed(title="Not Blacklisted",
                                    description=f"Asset `{asset_id}` is not in blacklist.",
                                    color=discord.Color.orange())
        else:
            if asset_blacklist.remove_asset(asset_id):
                embed = ModerationEmbed(title="✅ Asset Removed",
                                        description=f"Asset `{asset_id}` has been removed from blacklist.",
                                        color=discord.Color.green())
            else:
                embed = ModerationEmbed(title="❌ Failed",
                                        description=f"Failed to remove asset `{asset_id}`.",
                                        color=discord.Color.red())
    except Exception as e:
        embed = ModerationEmbed(title="❌ Error",
                                description=f"Error: {str(e)}",
                                color=discord.Color.red())

    await interaction.followup.send(embed=embed)


# ===== VIEWBLACKLIST COMMANDS =====
@tree.command(name="viewblacklist", description="View all blacklisted assets")
async def viewblacklist_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    try:
        assets = asset_blacklist.get_all_assets()

        embed = ModerationEmbed(title="Asset Blacklist",
                                description="List of blacklisted assets",
                                color=discord.Color.dark_purple())

        if assets:
            embed.add_field(name="Total Assets",
                            value=str(len(assets)),
                            inline=True)

            # Show first 10 assets
            asset_list = "\n".join([f"`{asset}`" for asset in assets[:10]])
            embed.add_field(name="Assets",
                            value=asset_list if asset_list else "None",
                            inline=False)

            if len(assets) > 10:
                embed.set_footer(text=f"And {len(assets)-10} more assets...")
        else:
            embed.add_field(name="Blacklist",
                            value="No assets are currently blacklisted.",
                            inline=False)

        await interaction.followup.send(embed=embed)
    except Exception as e:
        embed = ModerationEmbed(title="❌ Error",
                                description=f"Error: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== CHECKASSET COMMANDS =====
@tree.command(name="checkasset", description="Check if asset is blacklisted")
@app_commands.describe(asset_id="Asset ID to check")
async def checkasset_command(interaction: discord.Interaction, asset_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission.",
                                                ephemeral=True)
        return

    await interaction.response.defer()

    if not asset_id.isdigit():
        embed = ModerationEmbed(title="Invalid ID",
                                description="Asset ID must be numbers only.",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)
        return

    try:
        is_blacklisted = asset_blacklist.is_blacklisted(asset_id)

        if is_blacklisted:
            embed = ModerationEmbed(title="🔴 Blacklisted",
                                    description=f"Asset `{asset_id}` is blacklisted.",
                                    color=discord.Color.red())
        else:
            embed = ModerationEmbed(title="🟢 Allowed",
                                    description=f"Asset `{asset_id}` is not blacklisted.",
                                    color=discord.Color.green())
    except Exception as e:
        embed = ModerationEmbed(title="❌ Error",
                                description=f"Error: {str(e)}",
                                color=discord.Color.red())

    await interaction.followup.send(embed=embed)


# ===== CLEARBLACKLIST COMMANDS =====
@tree.command(name="clearblacklist", description="Clear all blacklisted assets (Admin)")
async def clearblacklist_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        assets = asset_blacklist.get_all_assets()
        count = len(assets)

        if count == 0:
            embed = ModerationEmbed(title="Blacklist Empty",
                                    description="No assets to clear.",
                                    color=discord.Color.orange())
        else:
            class ClearBlacklistView(View):
                def __init__(self, count: int, interaction_user: discord.User | discord.Member):
                    super().__init__(timeout=60)
                    self.count = count
                    self.interaction_user = interaction_user

                @discord.ui.button(label="Confirm Clear",
                                   style=discord.ButtonStyle.danger,
                                   emoji="🗑️")
                async def confirm(self, interaction: discord.Interaction, button: Button):
                    if interaction.user != self.interaction_user:
                        await interaction.response.send_message("Not your session.", ephemeral=True)
                        return

                    button.disabled = True
                    button.label = "Clearing..."
                    await interaction.response.edit_message(view=self)

                    try:
                        # This would need API support to clear all assets
                        # For now, we'll show a message
                        embed = ModerationEmbed(
                            title="⚠️ Feature Not Implemented",
                            description=f"This feature requires API support to clear all {self.count} assets.",
                            color=discord.Color.orange())
                        await interaction.edit_original_response(embed=embed, view=None)
                    except Exception as e:
                        await interaction.edit_original_response(
                            content=f"Error: {str(e)}", view=None)

                @discord.ui.button(label="Cancel",
                                   style=discord.ButtonStyle.secondary,
                                   emoji="✖️")
                async def cancel(self, interaction: discord.Interaction, button: Button):
                    if interaction.user != self.interaction_user:
                        await interaction.response.send_message("Not your session.", ephemeral=True)
                        return

                    await interaction.response.edit_message(content="Cancelled.", embed=None, view=None)

            embed = ModerationEmbed(
                title="Confirm Clear Blacklist",
                description=f"This will clear ALL {count} blacklisted assets.",
                color=discord.Color.red(),
                moderator=interaction.user)
            embed.add_field(name="Warning",
                            value="This action cannot be undone!",
                            inline=False)

            await interaction.followup.send(embed=embed,
                                            view=ClearBlacklistView(count, interaction.user))

    except Exception as e:
        embed = ModerationEmbed(title="❌ Error",
                                description=f"Error: {str(e)}",
                                color=discord.Color.red())
        await interaction.followup.send(embed=embed)


# ===== HELP COMMANDS =====
# ===== HWID COMMANDS =====

@tree.command(name="hwid_block", description="Block a device by HWID")
@app_commands.describe(hwid="The HWID to block")
async def hwid_block_command(interaction: discord.Interaction, hwid: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    try:
        res = requests.post(f"{API_URL}/hwid_block", json={"hwid": hwid}, timeout=5)
        if res.status_code == 200:
            embed = ModerationEmbed(title="✅ HWID Blocked", description=f"HWID `{hwid}` has been blocked.", color=discord.Color.red(), moderator=interaction.user)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to block HWID.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="hwid_unblock", description="Unblock a device by HWID")
@app_commands.describe(hwid="The HWID to unblock")
async def hwid_unblock_command(interaction: discord.Interaction, hwid: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    try:
        res = requests.post(f"{API_URL}/hwid_unblock", json={"hwid": hwid}, timeout=5)
        if res.status_code == 200:
            embed = ModerationEmbed(title="✅ HWID Unblocked", description=f"HWID `{hwid}` has been unblocked.", color=discord.Color.green(), moderator=interaction.user)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to unblock HWID.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="get_blocked_hwids", description="List all blocked HWIDs")
async def get_blocked_hwids_command(interaction: discord.Interaction):
    try:
        res = requests.get(f"{API_URL}/get_blocked_hwids", timeout=5)
        if res.status_code == 200:
            hwids = res.json().get("hwids", [])
            hwid_text = "\n".join([f"`{h}`" for h in hwids]) if hwids else "No blocked HWIDs."
            embed = ModerationEmbed(title="🚫 Blocked HWIDs", description=hwid_text, color=discord.Color.dark_grey(), moderator=interaction.user)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to fetch blocked HWIDs.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="get_player_hwid", description="Get the HWID of a player by their Roblox UserID")
@app_commands.describe(userid="Roblox UserID")
async def get_player_hwid_command(interaction: discord.Interaction, userid: str):
    try:
        res = requests.get(f"{API_URL}/get_player_hwid/{userid}", timeout=5)
        if res.status_code == 200:
            hwid = res.json().get("hwid")
            if hwid:
                embed = ModerationEmbed(title="🔍 Player HWID", description=f"UserID `{userid}` HWID: `{hwid}`", color=discord.Color.blue(), moderator=interaction.user)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ No HWID found for UserID `{userid}`.")
        else:
            await interaction.response.send_message("❌ Failed to fetch player HWID.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="get_players_by_hwid", description="Get all accounts associated with a specific HWID")
@app_commands.describe(hwid="The HWID to search")
async def get_players_by_hwid_command(interaction: discord.Interaction, hwid: str):
    try:
        res = requests.get(f"{API_URL}/get_players_by_hwid/{hwid}", timeout=5)
        if res.status_code == 200:
            users = res.json().get("users", [])
            users_text = ", ".join([f"`{u}`" for u in users]) if users else "No users found for this HWID."
            embed = ModerationEmbed(title="👥 Players by HWID", description=f"HWID: `{hwid}`\nUsers: {users_text}", color=discord.Color.blue(), moderator=interaction.user)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to fetch players by HWID.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="check_hwid", description="Check if a specific HWID is blocked")
@app_commands.describe(hwid="The HWID to check")
async def check_hwid_command(interaction: discord.Interaction, hwid: str):
    try:
        res = requests.get(f"{API_URL}/check_hwid/{hwid}", timeout=5)
        if res.status_code == 200:
            blocked = res.json().get("blocked", False)
            status = "🚫 Blocked" if blocked else "✅ Clear"
            embed = ModerationEmbed(title="🛡️ HWID Status", description=f"HWID: `{hwid}`\nStatus: {status}", color=discord.Color.orange() if blocked else discord.Color.green(), moderator=interaction.user)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to check HWID.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")


@tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = ModerationEmbed(
        title="Kynx SS 10 Commands Help",
        description="Game server moderation bot - Full command list",
        color=discord.Color.blue())

    embed.add_field(name="**Player Management**",
                    value="""`/kick [id] [reason]` - Kick player
`/mute [id] [duration] [reason]` - Mute player
`/umute [id]` - Remove mute
`/userlogs [id]` - View user logs
`/addnote [id] [note]` - Add note to player
`/userinfo [id]` - Get user info
`/gameinfo [placeid]` - Get game info""",
                    inline=False)

    embed.add_field(
        name="**Ban Commands**",
        value="""`/ban [id] [reason] [duration] [type]` - Ban player
`/unban [id] [type]` - Unban player
`/pcban [id] [reason]` - PC Ban player
`/unpcban [id]` - Remove PC ban
`/banasync [id] [reason]` - Async ban
`/unbanasync [id]` - Async unban
`/banlist` - View all bans (auto-saves)""",
        inline=False)

    embed.add_field(name="**Server Commands**",
                    value="""`/warn [id] [reason]` - Warn player
`/cleanotes [id]` - Remove all notes (Admin)
`/players` - Online players list
`/find [name]` - Find player
`/lookup [id]` - Player history
`/stats` - Server statistics
`/check` - Player count""",
                    inline=False)

    embed.add_field(name="**Asset Management**",
                    value="""`/blacklist [id]` - Block asset from scripts
`/unblacklist [id]` - Allow asset in scripts
`/viewblacklist` - List blocked assets
`/checkasset [id]` - Status of asset
`/clearblacklist` - Clear all (Admin)""",
                    inline=False)

    embed.add_field(name="**HWID Management**",
                    value="""`/hwid_block [hwid]` - Block device
`/hwid_unblock [hwid]` - Unblock device
`/get_blocked_hwids` - List blocked devices
`/get_player_hwid [id]` - Get player's HWID
`/get_players_by_hwid [hwid]` - Accounts by HWID
`/check_hwid [hwid]` - Check lock status""",
                    inline=False)

    embed.add_field(name="**Admin Commands**",
                    value="""`/restart` - Restart server
`/shutdown` - Stop server
`/announce [msg]` - Announcement
`/broadcast [msg]` - Broadcast
`/announcement [msg]` - Send announcement
`/logs [lines]` - View server logs""",
                    inline=False)

    embed.add_field(name="**Utility**",
                    value="""`/ping` - Bot status
`/check` - Server status""",
                    inline=False)

    embed.set_footer(
        text=
        f"Kynx SS 10 • Total commands: 37 • Auto-save Banlist: ✅ • Asset Blacklist: ✅ • PC Ban System: ✅"
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="cmds", description="Show all commands (short version)")
async def cmds_command(interaction: discord.Interaction):
    commands_list = """**Kynx SS 10 - Quick Commands List:**

**Player Management:**
`/mute [id] [duration] [reason]` - Mute player
`/umute [id]` - Remove mute `/kick`, `/userlogs`, `/addnote`, `/userinfo`, `/gameinfo`

**Ban Commands:**
`/ban`, `/unban`, `/pcban`, `/unpcban`, `/banasync`, `/unbanasync`, `/banlist`

**Server Commands:**
`/warn`, `/cleanotes`, `/players`, `/find`, `/lookup`, `/stats`, `/check`

**Asset Management:**
`/blacklist`, `/unblacklist`, `/viewblacklist`, `/checkasset`, `/clearblacklist`

**HWID Management:**
`/hwid_block`, `/hwid_unblock`, `/get_blocked_hwids`, `/get_player_hwid`, `/get_players_by_hwid`, `/check_hwid`

**Admin:**
`/restart`, `/shutdown`, `/announce`, `/broadcast`, `/announcement`, `/logs`

**Utility:**
`/ping`, `/check`"""

    embed = ModerationEmbed(title="Kynx SS 10 - Quick Commands",
                            description=commands_list,
                            color=discord.Color.blue())
    embed.set_footer(
        text="Use /help for detailed information • Total: 37 commands • Version: SS 10")
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No permission.", ephemeral=True)
    else:
        logger.error(f"Error: {str(error)}")
        await ctx.send("❌ Error.", ephemeral=True)


@bot.event
async def on_ready():
    logger.info(f"Kynx SS 10 ready: {bot.user}")
    try:
        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} global commands")

        command_names = [cmd.name for cmd in synced]
        logger.info(f"Synced commands: {', '.join(command_names)}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


def run():
    if TOKEN:
        logger.info("Starting Kynx SS 10 bot...")
        logger.info(f"Total commands loaded: 37")
        logger.info("Version: SS 10")
        logger.info("Mute/Umute commands: ✅ Fixed & Restored")
        logger.info("PC Ban system: ✅ Enabled")
        logger.info(
            f"Banlist Auto-save: ✅ ALWAYS enabled (saves to {BANLIST_DIR}/)")
        logger.info("Asset Blacklist: ✅ Integrated with API")
        bot.run(TOKEN)
    else:
        logger.error("No token found in .env file")


if __name__ == "__main__":
    run()