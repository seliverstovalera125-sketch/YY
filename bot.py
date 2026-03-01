import os
import discord
import requests
import logging
import asyncio
import json
import time
import hashlib
import base64
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID", "0"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0"))
API_URL = "https://a0077eee-c497-43f3-b189-c4c77d39fa4e-00-24uu76dd8yyu8.riker.replit.dev/"

BANLIST_DIR = "banlists"
LOGS_DIR = "logs"
CONFIG_DIR = "config"
TEMP_DIR = "temp"
ENCRYPTED_DIR = "encrypted_data"

for directory in [BANLIST_DIR, LOGS_DIR, CONFIG_DIR, TEMP_DIR, ENCRYPTED_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOGS_DIR, f'bot_{datetime.now().strftime("%Y%m%d")}.log'))
    ])
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
# intents.message_content = True # Disabled to avoid privileged intent error
# intents.members = True # Disabled to avoid privileged intent error
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ===== ENCRYPTION KEY =====
ENCRYPTION_KEY = hashlib.sha256(os.getenv("DISCORD_TOKEN", "default_key").encode()).digest()

# ===== CACHING =====
cache = {
    "bans": {"data": None, "timestamp": 0},
    "players": {"data": None, "timestamp": 0},
    "blacklist": {"data": None, "timestamp": 0},
    "settings": {"data": None, "timestamp": 0}
}
CACHE_TTL = 30  # seconds

# ===== RATE LIMITING =====
rate_limits = defaultdict(lambda: {"count": 0, "reset": time.time()})
RATE_LIMIT = 5  # commands per second
RATE_WINDOW = 1  # second

# ===== STATISTICS =====
command_stats = defaultdict(int)
user_command_stats = defaultdict(lambda: defaultdict(int))

# ===== ENCRYPTION FUNCTIONS =====
def encrypt_data(data: str) -> str:
    """Encrypt data to avoid detection"""
    encrypted = []
    for i, char in enumerate(data):
        key_char = ENCRYPTION_KEY[i % len(ENCRYPTION_KEY)]
        encrypted.append(chr(ord(char) ^ key_char))
    return base64.b64encode(''.join(encrypted).encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data"""
    try:
        decoded = base64.b64decode(encrypted_data).decode()
        decrypted = []
        for i, char in enumerate(decoded):
            key_char = ENCRYPTION_KEY[i % len(ENCRYPTION_KEY)]
            decrypted.append(chr(ord(char) ^ key_char))
        return ''.join(decrypted)
    except:
        return encrypted_data

def obfuscate_string(text: str) -> str:
    """Obfuscate sensitive strings"""
    return base64.b64encode(text.encode()).decode()

# ===== API CLIENT CLASS =====
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.last_request = 0
        self.min_interval = 0.5
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'X-Client-ID': hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        }

    def _rate_limit(self):
        now = time.time()
        if now - self.last_request < self.min_interval:
            time.sleep(self.min_interval - (now - self.last_request))
        self.last_request = time.time()

    def get(self, endpoint: str, params: Dict = None, use_cache: bool = False) -> Optional[Dict]:
        cache_key = endpoint.split('/')[1] if '/' in endpoint else endpoint

        if use_cache and cache.get(cache_key, {}).get("data"):
            cache_data = cache[cache_key]
            if time.time() - cache_data["timestamp"] < CACHE_TTL:
                return cache_data["data"]

        self._rate_limit()
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if use_cache:
                cache[cache_key] = {"data": data, "timestamp": time.time()}

            return data
        except Exception as e:
            logger.error(f"API GET error {endpoint}: {str(e)}")
            return None

    def post(self, endpoint: str, json: Dict = None) -> Optional[Dict]:
        self._rate_limit()
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=json,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API POST error {endpoint}: {str(e)}")
            return None

api = APIClient(API_URL)


# ===== ASSET BLACKLIST CLASS =====
class AssetBlacklist:
    def __init__(self):
        self._cache = {}
        self._pending_add = []
        self._pending_remove = []
        self._last_sync = 0
        self.sync_interval = 60
        self._storage_keys = {
            'list': obfuscate_string('blacklist_keys'),
            'asset': obfuscate_string('asset_data')
        }

    def is_blacklisted(self, asset_id: str) -> bool:
        if asset_id in self._cache:
            return self._cache[asset_id]

        try:
            endpoint = f"/is_blacklisted/{asset_id}"
            res = api.get(endpoint)
            if res:
                blacklisted = res.get('blacklisted', False)
                self._cache[asset_id] = blacklisted
                return blacklisted
        except:
            pass
        return False

    def add_asset(self, asset_id: str) -> bool:
        if asset_id not in self._pending_add:
            self._pending_add.append(asset_id)
        self._cache[asset_id] = True
        return True

    def remove_asset(self, asset_id: str) -> bool:
        if asset_id not in self._pending_remove:
            self._pending_remove.append(asset_id)
        self._cache[asset_id] = False
        return True

    def get_all_assets(self) -> List[str]:
        if self._cache:
            return list(self._cache.keys())

        data = api.get("/get_blacklist", use_cache=True)
        return data.get('assets', []) if data else []

    async def sync(self):
        now = time.time()
        if now - self._last_sync < self.sync_interval:
            return

        if self._pending_add:
            for asset_id in self._pending_add[:]:
                api.post("/add_blacklist", {"asset_id": asset_id})
                self._pending_add.remove(asset_id)

        if self._pending_remove:
            for asset_id in self._pending_remove[:]:
                api.post("/remove_blacklist", {"asset_id": asset_id})
                self._pending_remove.remove(asset_id)

        self._last_sync = now

asset_blacklist = AssetBlacklist()


# ===== LOCAL ENCRYPTED STORAGE =====
class LocalStorage:
    def __init__(self):
        self.data_file = os.path.join(ENCRYPTED_DIR, 'storage.enc')
        self.cache = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    encrypted_data = f.read()
                    decrypted = decrypt_data(encrypted_data)
                    self.cache = json.loads(decrypted)
            else:
                self.cache = {}
        except:
            self.cache = {}

    def save(self):
        try:
            data = json.dumps(self.cache)
            encrypted = encrypt_data(data)
            with open(self.data_file, 'w') as f:
                f.write(encrypted)
        except Exception as e:
            logger.error(f"Failed to save local storage: {e}")

    def get(self, key: str, default=None):
        return self.cache.get(key, default)

    def set(self, key: str, value):
        self.cache[key] = value
        self.save()

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
            self.save()

local_storage = LocalStorage()


# ===== ZERO TWO EMBED =====
class ZeroTwoEmbed(discord.Embed):
    def __init__(self, title, description, color=0xff69b4, target_user=None, moderator=None, **kwargs):
        super().__init__(
            title=f"🌸 {title} 🌸",
            description=f"```{description}```",
            color=color,
            timestamp=datetime.utcnow()
        )

        if target_user:
            self.add_field(name="🎯 Target", value=str(target_user), inline=True)
        if moderator:
            moderator_name = moderator.display_name if hasattr(moderator, 'display_name') else str(moderator)
            self.add_field(name="⚡ Moderator", value=moderator_name, inline=True)

        for key, value in kwargs.items():
            if value:
                self.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=True)

        self.set_footer(text=f"DARLING • Code:002 • v8.0.0")


# ===== PAGINATION VIEW =====
class PaginatorView(View):
    def __init__(self, items: List[Any], items_per_page: int = 5, title: str = "List"):
        super().__init__(timeout=120)
        self.items = items
        self.items_per_page = items_per_page
        self.current_page = 0
        self.title = title
        self.max_page = (len(items) - 1) // items_per_page
        self.message = None
        self.interaction_user = None

    def get_embed(self) -> ZeroTwoEmbed:
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(self.items))

        embed = ZeroTwoEmbed(
            title=self.title,
            description=f"Page {self.current_page + 1}/{self.max_page + 1} • Total: {len(self.items)}",
            color=0xff69b4
        )

        for i, item in enumerate(self.items[start:end], start=start + 1):
            if isinstance(item, dict):
                value = "\n".join([f"**{k}:** {v}" for k, v in item.items()])
                embed.add_field(name=f"#{i}", value=value, inline=False)
            else:
                embed.add_field(name=f"#{i}", value=str(item), inline=False)

        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.max_page:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()


# ===== CONFIRMATION VIEW =====
class ConfirmActionView(View):
    def __init__(self,
                 action: str,
                 userid: str,
                 reason: str,
                 username: str,
                 interaction_user: discord.User | discord.Member,
                 duration: int = -1,
                 is_admin=False,
                 ban_type: str = "normal",
                 extra_data: Dict = None):
        super().__init__(timeout=60)
        self.action = action
        self.userid = userid
        self.reason = reason
        self.username = username
        self.duration = duration
        self.interaction_user = interaction_user
        self.is_admin = is_admin
        self.ban_type = ban_type
        self.extra_data = extra_data or {}

    @discord.ui.button(label="Confirm DARLING",
                       style=discord.ButtonStyle.danger,
                       emoji="💕")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("This is not your session, DARLING~", ephemeral=True)
            return

        button.disabled = True
        button.label = "Processing..."
        await interaction.response.edit_message(view=self)

        try:
            command_stats[self.action] += 1
            user_command_stats[interaction.user.id][self.action] += 1

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
                if self.extra_data.get("ban_linked"):
                    data["ban_linked"] = True
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
            logger.info(f"API Response: {response.status_code} - {response.text}")

            if self.action == "ban":
                duration_text = "permanently" if self.duration == -1 else f"for {self.duration} days"
                ban_type_text = "PC " if self.ban_type == "pc" else ""

                embed = ZeroTwoEmbed(
                    title=f"✅ {ban_type_text}Ban Executed",
                    description=f"**{self.username}** has been {ban_type_text}banned {duration_text}.",
                    color=0xff69b4,
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user,
                    reason=self.reason
                )

                if self.ban_type == "pc":
                    embed.add_field(name="💻 Type", value="PC Ban (Device-based)", inline=True)

                if self.extra_data.get("ban_linked"):
                    embed.add_field(name="🔗 Linked Accounts", value="All linked accounts were also banned", inline=True)

            elif self.action == "pcban":
                embed = ZeroTwoEmbed(
                    title="✅ PC Ban Executed",
                    description=f"**{self.username}** has been PC banned (permanent).",
                    color=0x8b0000,
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user,
                    reason=self.reason,
                    type="PC Ban (Device-based)",
                    status="Permanent"
                )

            elif self.action == "kick":
                embed = ZeroTwoEmbed(
                    title="✅ Kick Executed",
                    description=f"**{self.username}** has been kicked.",
                    color=0xff1493,
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user,
                    reason=self.reason
                )

            elif self.action == "mute":
                embed = ZeroTwoEmbed(
                    title="✅ Mute Executed",
                    description=f"**{self.username}** has been muted for {self.duration} minutes.",
                    color=0xff69b4,
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user,
                    reason=self.reason
                )

            elif self.action == "umute":
                embed = ZeroTwoEmbed(
                    title="✅ Unmute Executed",
                    description=f"**{self.username}** has been unmuted.",
                    color=0x00ff00,
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user
                )

            elif self.action == "warn":
                embed = ZeroTwoEmbed(
                    title="✅ Warn Executed",
                    description=f"**{self.username}** has been warned.",
                    color=0xffa500,
                    target_user=f"{self.username} ({self.userid})",
                    moderator=interaction.user,
                    reason=self.reason
                )

            elif self.action == "restart":
                embed = ZeroTwoEmbed(
                    title="🔄 Server Restarting",
                    description="Server restart command sent.",
                    color=0xffa500,
                    moderator=interaction.user
                )

            elif self.action == "shutdown":
                embed = ZeroTwoEmbed(
                    title="🛑 Server Shutdown",
                    description="Server shutdown command sent.",
                    color=0x8b0000,
                    moderator=interaction.user
                )

            elif self.action == "announce":
                embed = ZeroTwoEmbed(
                    title="📢 Announcement Sent",
                    description="Announcement has been sent to all players.",
                    color=0x00ff00,
                    moderator=interaction.user,
                    message=self.reason
                )

            elif self.action == "broadcast":
                embed = ZeroTwoEmbed(
                    title="📡 Broadcast Sent",
                    description="Broadcast sent to all players.",
                    color=0x0000ff,
                    moderator=interaction.user,
                    message=self.reason
                )

            else:
                embed = ZeroTwoEmbed(
                    title="✅ Action Completed",
                    description=f"Command executed: {self.action}",
                    color=0xff69b4,
                    moderator=interaction.user
                )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except requests.exceptions.ConnectionError:
            await interaction.edit_original_response(content="Failed to connect to game server, DARLING~", view=None)
        except requests.exceptions.Timeout:
            await interaction.edit_original_response(content="Server timeout... Zero Two is waiting~", view=None)
        except Exception as e:
            logger.error(f"Error in confirm action: {str(e)}")
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("This is not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Action cancelled.", embed=None, view=None)


# ===== ENHANCED BANLIST VIEW =====
class EnhancedBanListView(View):
    def __init__(self, bans: list, interaction_user: discord.User | discord.Member):
        super().__init__(timeout=300)
        self.bans = bans
        self.page = 0
        self.items_per_page = 5
        self.total_pages = max(1, (len(bans) + self.items_per_page - 1) // self.items_per_page)
        self.interaction_user = interaction_user
        self.filter_type = "all"  # all, normal, pc
        self.filter_duration = "all"  # all, permanent, temporary
        self.sort_by = "date_desc"  # date_desc, date_asc, name_asc, name_desc
        self._update_buttons()

    def _update_buttons(self):
        self.previous_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= self.total_pages - 1

    def _filter_bans(self) -> list:
        filtered = self.bans

        if self.filter_type != "all":
            filtered = [b for b in filtered if b.get('banType') == self.filter_type]

        if self.filter_duration != "all":
            if self.filter_duration == "permanent":
                filtered = [b for b in filtered if b.get('duration', -1) == -1]
            elif self.filter_duration == "temporary":
                filtered = [b for b in filtered if b.get('duration', -1) > 0]

        if self.sort_by == "date_desc":
            filtered.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        elif self.sort_by == "date_asc":
            filtered.sort(key=lambda x: x.get('timestamp', 0))
        elif self.sort_by == "name_asc":
            filtered.sort(key=lambda x: x.get('username', '').lower())
        elif self.sort_by == "name_desc":
            filtered.sort(key=lambda x: x.get('username', '').lower(), reverse=True)

        return filtered

    def get_embed(self) -> ZeroTwoEmbed:
        filtered = self._filter_bans()
        start = self.page * self.items_per_page
        end = min(start + self.items_per_page, len(filtered))
        total_filtered = len(filtered)

        stats = {
            "total": len(self.bans),
            "normal": sum(1 for b in self.bans if b.get('banType') != 'pc'),
            "pc": sum(1 for b in self.bans if b.get('banType') == 'pc'),
            "permanent": sum(1 for b in self.bans if b.get('duration', -1) == -1),
            "temporary": sum(1 for b in self.bans if b.get('duration', -1) > 0)
        }

        embed = ZeroTwoEmbed(
            title="🔨 Zero Two's Ban List",
            description=f"Total bans: {stats['total']} (N:{stats['normal']} | PC:{stats['pc']} | P:{stats['permanent']} | T:{stats['temporary']})",
            color=0x8b0000
        )

        if not filtered:
            embed.add_field(name="No bans", value="No bans match the current filters.", inline=False)
            return embed

        for i in range(start, end):
            ban = filtered[i]
            userid = ban.get('userid', 'Unknown')
            username = ban.get('username', 'Unknown')
            display_name = ban.get('display_name', username)
            reason = ban.get('reason', 'No reason')
            executor = ban.get('executor', 'Unknown')
            timestamp = ban.get('timestamp', 0)
            duration = ban.get('duration', -1)
            ban_type = ban.get('banType', 'normal')

            duration_text = "Permanent" if duration == -1 else f"{duration} days"

            if timestamp:
                try:
                    date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = str(timestamp)
            else:
                date_str = "N/A"

            ban_type_icon = "💻" if ban_type == "pc" else ""
            ban_type_text = "PC Ban" if ban_type == "pc" else "Normal"
            user_display = f"{username} (@{display_name})" if display_name != username else username

            embed.add_field(
                name=f"#{i+1} {ban_type_icon} {user_display}",
                value=f"ID: `{userid}`\nReason: {reason}\nDuration: {duration_text}\nType: {ban_type_text}\nBy: {executor}\nDate: {date_str}",
                inline=False
            )

        embed.set_footer(text=f"Page {self.page+1}/{self.total_pages} | Filter: {self.filter_type} | Sort: {self.sort_by}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        if self.page > 0:
            self.page -= 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        if self.page < self.total_pages - 1:
            self.page += 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.select(
        placeholder="Filter by type",
        options=[
            discord.SelectOption(label="All Types", value="all", emoji="📋"),
            discord.SelectOption(label="Normal Bans", value="normal", emoji="🔨"),
            discord.SelectOption(label="PC Bans", value="pc", emoji="💻")
        ]
    )
    async def filter_type(self, interaction: discord.Interaction, select: Select):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        self.filter_type = select.values[0]
        self.page = 0
        self.total_pages = max(1, (len(self._filter_bans()) + self.items_per_page - 1) // self.items_per_page)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.select(
        placeholder="Filter by duration",
        options=[
            discord.SelectOption(label="All Durations", value="all", emoji="📋"),
            discord.SelectOption(label="Permanent", value="permanent", emoji="⏰"),
            discord.SelectOption(label="Temporary", value="temporary", emoji="⏳")
        ]
    )
    async def filter_duration(self, interaction: discord.Interaction, select: Select):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        self.filter_duration = select.values[0]
        self.page = 0
        self.total_pages = max(1, (len(self._filter_bans()) + self.items_per_page - 1) // self.items_per_page)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.select(
        placeholder="Sort by",
        options=[
            discord.SelectOption(label="Date (Newest)", value="date_desc", emoji="📅"),
            discord.SelectOption(label="Date (Oldest)", value="date_asc", emoji="📅"),
            discord.SelectOption(label="Name (A-Z)", value="name_asc", emoji="🔤"),
            discord.SelectOption(label="Name (Z-A)", value="name_desc", emoji="🔤")
        ]
    )
    async def sort_by_select(self, interaction: discord.Interaction, select: Select):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        self.sort_by = select.values[0]
        self.page = 0
        self.total_pages = max(1, (len(self._filter_bans()) + self.items_per_page - 1) // self.items_per_page)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
                        ban['display_name'] = username

                enriched_bans.append(ban)

            self.bans = enriched_bans
            self.page = 0
            self.total_pages = max(1, (len(self._filter_bans()) + self.items_per_page - 1) // self.items_per_page)
            self._update_buttons()

            await interaction.edit_original_response(embed=self.get_embed(), view=self)

        except Exception as e:
            logger.error(f"Failed to refresh banlist: {str(e)}")
            await interaction.followup.send("Failed to refresh, DARLING~", ephemeral=True)

    @discord.ui.button(label="💾 Save", style=discord.ButtonStyle.success)
    async def save(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            saved_files = save_banlist_to_disk(self.bans, "both")
            embed = ZeroTwoEmbed(
                title="✅ Banlist Saved",
                description=f"Banlist saved to disk",
                color=0x00ff00,
                moderator=interaction.user
            )
            embed.add_field(name="📁 JSON", value=f"`{os.path.basename(saved_files['json'])}`", inline=True)
            embed.add_field(name="📄 TXT", value=f"`{os.path.basename(saved_files['txt'])}`", inline=True)

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Failed to save: {str(e)}", ephemeral=True)

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.message.delete()


# ===== UNBAN VIEW =====
class UnbanView(View):
    def __init__(self, userid: str, username: str, display_name: str,
                 interaction_user: discord.User | discord.Member, ban_type: str = "normal"):
        super().__init__(timeout=60)
        self.userid = userid
        self.username = username
        self.interaction_user = interaction_user
        self.ban_type = ban_type

    @discord.ui.button(label="Confirm Unban",
                       style=discord.ButtonStyle.success,
                       emoji="✅")
    async def confirm_unban(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=data, timeout=10)
            response.raise_for_status()

            ban_type_text = "PC " if self.ban_type == "pc" else ""

            embed = ZeroTwoEmbed(
                title=f"✅ {ban_type_text}Unbanned",
                description=f"**{self.username}** has been {ban_type_text}unbanned.",
                color=0x00ff00,
                target_user=f"{self.username} ({self.userid})",
                moderator=interaction.user
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            logger.error(f"Failed to unban: {str(e)}")
            await interaction.edit_original_response(content=f"Failed to unban: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Cancelled.", embed=None, view=None)


# ===== NOTE VIEW =====
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
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=note_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="Note Added",
                description=f"**{self.username}** has a new note.",
                color=0x00ff00,
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user,
                note=self.note
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Note cancelled.", embed=None, view=None)


# ===== CLEAN NOTES VIEW =====
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
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=clean_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="Notes Cleaned",
                description=f"All notes for **{self.username}** have been removed.",
                color=0x00ff00,
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Clean notes cancelled.", embed=None, view=None)


# ===== ANNOUNCE VIEW =====
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
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=announce_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="Announcement Sent",
                description="Announcement has been sent to all players.",
                color=0x00ff00,
                moderator=interaction.user,
                message=self.message
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Announcement cancelled.", embed=None, view=None)


# ===== BROADCAST VIEW =====
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
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=broadcast_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="Broadcast Sent",
                description="Message broadcasted to all players.",
                color=0x0000ff,
                moderator=interaction.user,
                message=self.message
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Broadcast cancelled.", embed=None, view=None)


# ===== WARN VIEW =====
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
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=warning_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="Player Warned",
                description=f"**{self.username}** has been warned.",
                color=0xffa500,
                target_user=f"{self.username} ({self.userid})",
                moderator=interaction.user,
                reason=self.reason
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Warn cancelled.", embed=None, view=None)


# ===== PC BAN VIEW =====
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
            await interaction.response.send_message("This is not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=pcban_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="PC Ban Executed",
                description=f"**{self.username}** has been PC banned.",
                color=0x8b0000,
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user,
                reason=self.reason,
                type="PC Ban (Device-based)",
                status="Permanent"
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            logger.error(f"PC ban error: {str(e)}")
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("This is not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="PC Ban cancelled.", embed=None, view=None)


# ===== UNPC BAN VIEW =====
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
            await interaction.response.send_message("This is not your session, DARLING~", ephemeral=True)
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
            response = requests.post(f"{API_URL}/send_command", json=unpcban_data, timeout=10)
            response.raise_for_status()

            embed = ZeroTwoEmbed(
                title="PC Unban Executed",
                description=f"**{self.username}** has been PC unbanned.",
                color=0x00ff00,
                target_user=f"{self.username} (@{self.display_name})",
                moderator=interaction.user,
                type="PC Unban (Device-based)",
                note="The player can now join from previously banned devices."
            )

            await interaction.edit_original_response(content=None, embed=embed, view=None)

        except Exception as e:
            logger.error(f"PC unban error: {str(e)}")
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("This is not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="PC Unban cancelled.", embed=None, view=None)


# ===== CLEAR BLACKLIST VIEW =====
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
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        button.disabled = True
        button.label = "Clearing..."
        await interaction.response.edit_message(view=self)

        try:
            cleared = 0
            assets = asset_blacklist.get_all_assets()
            for asset_id in assets:
                if asset_blacklist.remove_asset(asset_id):
                    cleared += 1

            await asset_blacklist.sync()

            embed = ZeroTwoEmbed(
                title="✅ Blacklist Cleared",
                description=f"Successfully cleared {cleared} assets.",
                color=0x00ff00,
                moderator=interaction.user
            )
            await interaction.edit_original_response(embed=embed, view=None)
        except Exception as e:
            await interaction.edit_original_response(content=f"Error: {str(e)}", view=None)

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.secondary,
                       emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.response.edit_message(content="Cancelled.", embed=None, view=None)


# ===== STATS VIEW =====
class StatsView(View):
    def __init__(self, interaction_user: discord.User | discord.Member):
        super().__init__(timeout=60)
        self.interaction_user = interaction_user
        self.current_page = 0

    def get_embed(self) -> ZeroTwoEmbed:
        if self.current_page == 0:
            embed = ZeroTwoEmbed(
                title="📊 Command Statistics",
                description="Most used commands",
                color=0x800080,
                moderator=self.interaction_user
            )

            sorted_commands = sorted(command_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            for cmd, count in sorted_commands:
                embed.add_field(name=f"/{cmd}", value=f"{count} times", inline=True)
        else:
            embed = ZeroTwoEmbed(
                title="👤 User Statistics",
                description="Most active users",
                color=0x800080,
                moderator=self.interaction_user
            )

            user_totals = {}
            for user_id, commands in user_command_stats.items():
                user_totals[user_id] = sum(commands.values())

            sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)[:10]
            for user_id, count in sorted_users:
                embed.add_field(name=f"User {user_id}", value=f"{count} commands", inline=True)

        embed.set_footer(text=f"Page {self.current_page + 1}/2")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        if self.current_page < 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("Not your session, DARLING~", ephemeral=True)
            return

        await interaction.message.delete()


# ===== AUTHORIZATION FUNCTIONS =====
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


def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    user_limit = rate_limits[user_id]

    if now > user_limit["reset"]:
        user_limit["count"] = 0
        user_limit["reset"] = now + RATE_WINDOW

    user_limit["count"] += 1
    return user_limit["count"] <= RATE_LIMIT


# ===== BANLIST SAVE FUNCTION =====
def save_banlist_to_disk(bans: list, format: str = "both") -> Dict[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = {}

    data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_bans": len(bans),
            "server": "Zero Two's Server",
            "version": "Code:002",
            "format_version": "2.0"
        },
        "statistics": {
            "normal_bans": sum(1 for b in bans if b.get('banType') != 'pc'),
            "pc_bans": sum(1 for b in bans if b.get('banType') == 'pc'),
            "permanent_bans": sum(1 for b in bans if b.get('duration', -1) == -1),
            "temporary_bans": sum(1 for b in bans if b.get('duration', -1) > 0)
        },
        "bans": bans
    }

    if format in ["json", "both"]:
        filename = f"banlist_{timestamp}.json"
        filepath = os.path.join(BANLIST_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        saved_files['json'] = filepath

    if format in ["txt", "both"]:
        txt_filename = f"banlist_{timestamp}.txt"
        txt_filepath = os.path.join(BANLIST_DIR, txt_filename)

        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f" ZERO TWO'S BAN LIST ".center(80, '=') + "\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {data['metadata']['generated']}\n")
            f.write(f"Total bans: {data['metadata']['total_bans']}\n")
            f.write(f"Normal bans: {data['statistics']['normal_bans']}\n")
            f.write(f"PC bans: {data['statistics']['pc_bans']}\n")
            f.write(f"Permanent: {data['statistics']['permanent_bans']}\n")
            f.write(f"Temporary: {data['statistics']['temporary_bans']}\n")
            f.write("=" * 80 + "\n\n")

            if not bans:
                f.write("No bans found. DARLING~\n")
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

                    if timestamp_ban:
                        try:
                            date_str = datetime.fromtimestamp(timestamp_ban).strftime('%Y-%m-%d %H:%M')
                        except:
                            date_str = str(timestamp_ban)
                    else:
                        date_str = "N/A"

                    duration_text = "Permanent" if duration == -1 else f"{duration} days"
                    ban_type_text = "💻 PC Ban" if ban_type == "pc" else "Normal Ban"
                    user_display = f"{username} (@{display_name})" if display_name != username else username

                    f.write(f"\n{'─' * 80}\n")
                    f.write(f"#{i:4d} | {ban_type_text:12} | {user_display}\n")
                    f.write(f"      ID: {userid}\n")
                    f.write(f"      Reason: {reason}\n")
                    f.write(f"      Duration: {duration_text}\n")
                    f.write(f"      Banned by: {executor}\n")
                    f.write(f"      Date: {date_str}\n")

        saved_files['txt'] = txt_filepath

    logger.info(f"Banlist saved: {', '.join(saved_files.values())}")
    return saved_files


# ===== ROBLOX API FUNCTIONS =====
async def get_roblox_user_data(userid: str) -> Optional[Dict]:
    cache_key = f"roblox_user_{userid}"

    if cache_key in cache:
        cache_data = cache[cache_key]
        if time.time() - cache_data["timestamp"] < 300:
            return cache_data["data"]

    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{userid}", timeout=5)
        if res.status_code != 200:
            return None
        data = res.json()

        thumb_res = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png",
            timeout=5
        )
        avatar = None
        if thumb_res.status_code == 200:
            avatar = thumb_res.json()["data"][0]["imageUrl"]

        result = {
            "name": data["name"],
            "display": data["displayName"],
            "avatar": avatar,
            "created": data.get("created", "Unknown")
        }

        cache[cache_key] = {"data": result, "timestamp": time.time()}
        return result
    except Exception as e:
        logger.error(f"Error getting Roblox user data: {str(e)}")
        return None


async def get_roblox_game_data(placeid: str) -> Optional[Dict]:
    try:
        response = requests.get(
            f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={placeid}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                game = data[0]

                icon_res = requests.get(
                    f"https://thumbnails.roblox.com/v1/places/gameicons?placeIds={placeid}&size=512x512&format=Png",
                    timeout=5
                )
                icon = None
                if icon_res.status_code == 200:
                    icon_data = icon_res.json()
                    if icon_data.get("data") and len(icon_data["data"]) > 0:
                        icon = icon_data["data"][0]["imageUrl"]

                return {
                    "name": game.get('name', 'Unknown'),
                    "description": game.get('description', 'No description'),
                    "icon": icon,
                    "url": f"https://www.roblox.com/games/{placeid}"
                }
        return None
    except Exception as e:
        logger.error(f"Error getting game data: {str(e)}")
        return None


def check_api() -> bool:
    try:
        response = requests.get(f"{API_URL}/get_players", timeout=5)
        return response.status_code == 200
    except:
        return False


# ===== BACKGROUND TASKS =====
@tasks.loop(minutes=5)
async def sync_blacklist():
    await asset_blacklist.sync()
    local_storage.save()


@tasks.loop(minutes=1)
async def update_cache():
    api.get("/get_players", use_cache=False)
    api.get("/get_bans", use_cache=False)


@tasks.loop(hours=1)
async def cleanup_temp_files():
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        if os.path.getmtime(filepath) < now - 86400:
            os.remove(filepath)
            logger.info(f"Removed old temp file: {filename}")


# ===== PLAYER MANAGEMENT COMMANDS =====

@tree.command(name="kick", description="Kick a player from the Roblox server")
@app_commands.describe(userid="Roblox UserID", reason="Kick reason")
async def kick_command(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    embed = ZeroTwoEmbed(
        title="Confirm Kick",
        description=f"Kick **{data['name']}**?",
        color=0xffa500,
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="💢 Reason", value=reason, inline=True)

    await interaction.followup.send(
        embed=embed,
        view=ConfirmActionView("kick", userid, reason, data['name'], interaction.user)
    )


@tree.command(name="mute", description="Mute a player")
@app_commands.describe(
    userid="Roblox UserID",
    duration="Duration in minutes (e.g. 10, 60, 1440)",
    reason="Reason for the mute"
)
async def mute_command(interaction: discord.Interaction, userid: str, duration: int, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"

    embed = ZeroTwoEmbed(
        title="Confirm Mute",
        description=f"Mute **{username}**?",
        color=0xffa500,
        target_user=f"{username} ({userid})",
        moderator=interaction.user
    )
    embed.add_field(name="⏰ Duration", value=f"{duration} minutes", inline=True)
    embed.add_field(name="💢 Reason", value=reason, inline=True)

    await interaction.followup.send(
        embed=embed,
        view=ConfirmActionView("mute", userid, reason, username, interaction.user, duration=duration)
    )


@tree.command(name="umute", description="Unmute a player")
@app_commands.describe(userid="Roblox UserID")
async def umute_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"

    embed = ZeroTwoEmbed(
        title="Confirm Unmute",
        description=f"Unmute **{username}**?",
        color=0x00ff00,
        target_user=f"{username} ({userid})",
        moderator=interaction.user
    )

    await interaction.followup.send(
        embed=embed,
        view=ConfirmActionView("umute", userid, "Unmuted via Discord", username, interaction.user)
    )


@tree.command(name="userlogs", description="Displays a user's moderation logs")
@app_commands.describe(userid="Roblox UserID", limit="Number of logs to show (default: 10)")
async def userlogs_command(interaction: discord.Interaction, userid: str, limit: int = 10):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"
    avatar = data['avatar'] if data else None

    try:
        response = requests.get(f"{API_URL}/user_logs?userid={userid}", timeout=10)

        embed = ZeroTwoEmbed(
            title="User Logs",
            description=f"Moderation history for **{username}**",
            color=0x0000ff,
            target_user=f"{username} ({userid})",
            moderator=interaction.user
        )

        if avatar:
            embed.set_thumbnail(url=avatar)

        embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)

        if response.status_code == 200:
            logs = response.json()
            if logs and len(logs) > 0:
                for i, log in enumerate(logs[:limit]):
                    embed.add_field(
                        name=f"{log.get('action', 'Action').title()} - {log.get('date', 'Unknown')}",
                        value=f"**Reason:** {log.get('reason', 'No reason')}\n**Moderator:** {log.get('moderator', 'Unknown')}",
                        inline=False
                    )
                if len(logs) > limit:
                    embed.set_footer(text=f"And {len(logs)-limit} more logs... • Zero Two")
            else:
                embed.add_field(name="No Logs", value="No moderation logs found for this user.", inline=False)
        else:
            embed.add_field(name="Logs Unavailable", value="Could not fetch logs from server.", inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ZeroTwoEmbed(title="Error", description=f"Cannot get user logs: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="addnote", description="Add a note to a player")
@app_commands.describe(userid="Roblox UserID", note="Note to add")
async def addnote_command(interaction: discord.Interaction, userid: str, note: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    embed = ZeroTwoEmbed(
        title="Confirm Note",
        description=f"Add note to **{data['name']}**?",
        color=0x0000ff,
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="📝 Note", value=note, inline=False)

    await interaction.followup.send(
        embed=embed,
        view=NoteView(userid, note, data['name'], data['display'], interaction.user)
    )


@tree.command(name="userinfo", description="Display information about a user on Roblox")
@app_commands.describe(userid="Roblox UserID")
async def userinfo_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    is_banned = False
    ban_reason = ""
    ban_type = "normal"
    ban_date = ""

    try:
        bans_res = requests.get(f"{API_URL}/get_bans", timeout=5)
        if bans_res.status_code == 200:
            bans = bans_res.json()
            for ban in bans:
                if str(ban.get('userid')) == userid:
                    is_banned = True
                    ban_reason = ban.get('reason', 'No reason')
                    ban_type = ban.get('banType', 'normal')
                    if ban.get('timestamp'):
                        ban_date = datetime.fromtimestamp(ban['timestamp']).strftime('%Y-%m-%d %H:%M')
                    break
    except:
        pass

    linked_count = 0
    suspicious_score = 0

    try:
        check_res = requests.post(
            f"{API_URL}/send_command",
            json={"command": "check_suspicious", "userid": userid},
            timeout=5
        )
        if check_res.status_code == 200:
            check_data = check_res.json()
            linked_count = len(check_data.get('linkedAccounts', []))
            suspicious_score = check_data.get('suspiciousScore', 0)
    except:
        pass

    embed = ZeroTwoEmbed(
        title="User Information",
        description=f"Roblox profile information",
        color=0xff69b4
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="👤 Username", value=data['name'], inline=True)
    embed.add_field(name="✨ Display Name", value=data['display'], inline=True)
    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="📅 Account Created", value=data.get('created', 'Unknown'), inline=True)

    if is_banned:
        ban_status = "Banned"
        if ban_type == "pc":
            ban_status = "💻 PC Banned"
        embed.add_field(name="🚫 Ban Status", value=ban_status, inline=True)
        embed.add_field(name="💢 Ban Reason", value=ban_reason, inline=False)
        embed.add_field(name="🔰 Ban Type", value="PC Ban" if ban_type == "pc" else "Normal Ban", inline=True)
        if ban_date:
            embed.add_field(name="📆 Ban Date", value=ban_date, inline=True)
    else:
        embed.add_field(name="🚫 Ban Status", value="✅ Not banned", inline=True)

    if linked_count > 0:
        embed.add_field(name="🔗 Linked Accounts", value=str(linked_count), inline=True)

    if suspicious_score > 0:
        embed.add_field(name="⚠️ Suspicious Score", value=str(suspicious_score), inline=True)

    await interaction.followup.send(embed=embed)


@tree.command(name="gameinfo", description="Display the info of a Roblox game")
@app_commands.describe(placeid="Roblox Place ID")
async def gameinfo_command(interaction: discord.Interaction, placeid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not placeid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid Place ID", description="Place ID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    game_data = await get_roblox_game_data(placeid)

    if not game_data:
        embed = ZeroTwoEmbed(title="Game Not Found", description=f"Place ID `{placeid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    embed = ZeroTwoEmbed(
        title="🎮 Game Information",
        description=f"**{game_data['name']}**",
        color=0x800080
    )

    if game_data.get('icon'):
        embed.set_thumbnail(url=game_data['icon'])

    embed.add_field(name="🆔 Place ID", value=f"`{placeid}`", inline=True)
    embed.add_field(name="📛 Name", value=game_data['name'], inline=True)
    embed.add_field(name="📝 Description", value=game_data['description'][:100] + "...", inline=False)
    embed.add_field(name="🔗 URL", value=f"[Click here]({game_data['url']})", inline=False)

    try:
        players_res = requests.get(f"{API_URL}/get_players", timeout=5)
        if players_res.status_code == 200:
            players_data = players_res.json()
            player_count = players_data.get('count', 0)
            embed.add_field(name="👥 Current Players", value=str(player_count), inline=True)
    except:
        pass

    await interaction.followup.send(embed=embed)


# ===== BAN COMMANDS =====

@tree.command(name="ban", description="Ban a player")
@app_commands.describe(
    userid="Roblox UserID",
    reason="Ban reason",
    duration="Ban duration in days (default: -1 for permanent)",
    ban_type="Ban type: normal or pc",
    ban_linked="Also ban linked accounts (default: False)"
)
async def ban_command(
    interaction: discord.Interaction,
    userid: str,
    reason: str,
    duration: int = -1,
    ban_type: str = "normal",
    ban_linked: bool = False
):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    duration_text = "permanent" if duration == -1 else f"{duration} days"

    if ban_type not in ["normal", "pc"]:
        ban_type = "normal"

    ban_type_display = "PC Ban" if ban_type == "pc" else "Normal Ban"

    embed = ZeroTwoEmbed(
        title=f"Confirm {ban_type_display}",
        description=f"{ban_type_display} **{data['name']}**?",
        color=0x8b0000 if ban_type == "pc" else 0xffa500,
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="💢 Reason", value=reason, inline=True)
    embed.add_field(name="⏰ Duration", value=duration_text, inline=True)
    embed.add_field(name="🔰 Type", value=ban_type_display, inline=True)

    if ban_linked:
        embed.add_field(name="🔗 Linked Accounts", value="Will also ban linked accounts", inline=True)

    await interaction.followup.send(
        embed=embed,
        view=ConfirmActionView(
            "ban",
            userid,
            reason,
            data['name'],
            interaction.user,
            duration,
            ban_type=ban_type,
            extra_data={"ban_linked": ban_linked}
        )
    )


@tree.command(name="unban", description="Unban a player")
@app_commands.describe(
    userid="Roblox UserID to unban",
    ban_type="Ban type to unban: normal or pc (default: auto-detect)"
)
async def unban_command(interaction: discord.Interaction, userid: str, ban_type: str = "auto"):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
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
            embed = ZeroTwoEmbed(title="Not banned", description=f"UserID `{userid}` is not banned.", color=0xffa500)
            await interaction.followup.send(embed=embed)
            return

        roblox_data = await get_roblox_user_data(userid)
        username = roblox_data['name'] if roblox_data else user_ban.get('username', 'Unknown')

        detected_ban_type = user_ban.get('banType', 'normal')
        if ban_type != "auto":
            detected_ban_type = ban_type

        embed = ZeroTwoEmbed(
            title=f"Confirm {'PC ' if detected_ban_type == 'pc' else ''}Unban",
            description=f"{'PC ' if detected_ban_type == 'pc' else ''}Unban **{username}**?",
            color=0xffd700,
            target_user=f"{username} ({userid})",
            moderator=interaction.user
        )

        embed.add_field(name="💢 Ban Reason", value=user_ban.get('reason', 'No reason'), inline=False)
        embed.add_field(name="👤 Banned By", value=user_ban.get('executor', 'Unknown'), inline=True)
        embed.add_field(name="🔰 Ban Type", value="PC Ban" if detected_ban_type == "pc" else "Normal Ban", inline=True)

        if roblox_data and roblox_data['avatar']:
            embed.set_thumbnail(url=roblox_data['avatar'])

        view = UnbanView(userid, username, "", interaction.user, detected_ban_type)
        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        logger.error(f"Error in unban command: {str(e)}")
        embed = ZeroTwoEmbed(title="Error", description="Cannot process unban.", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="pcban", description="PC Ban player (Device-based ban)")
@app_commands.describe(userid="Roblox UserID", reason="Ban reason")
async def pcban_command(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    try:
        response = requests.get(f"{API_URL}/get_bans", timeout=10)
        if response.status_code == 200:
            bans = response.json()
            for ban in bans:
                if str(ban.get('userid')) == userid:
                    embed = ZeroTwoEmbed(
                        title="Already Banned",
                        description=f"**{data['name']}** is already banned.",
                        color=0xffa500,
                        target_user=f"{data['name']} (@{data['display']})",
                        moderator=interaction.user
                    )
                    embed.add_field(name="💢 Current Ban Reason", value=ban.get('reason', 'No reason'), inline=False)
                    embed.add_field(name="👤 Banned By", value=ban.get('executor', 'Unknown'), inline=True)
                    embed.add_field(
                        name="🔰 Ban Type",
                        value="PC Ban" if ban.get('banType') == 'pc' else 'Normal Ban',
                        inline=True
                    )
                    await interaction.followup.send(embed=embed)
                    return
    except:
        pass

    embed = ZeroTwoEmbed(
        title="Confirm PC Ban",
        description=f"PC Ban **{data['name']}**?",
        color=0x8b0000,
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="💢 Reason", value=reason, inline=True)
    embed.add_field(name="💻 Ban Type", value="PC Ban (Device-based)", inline=True)
    embed.add_field(
        name="⚠️ Warning",
        value="PC bans are device-based and permanent. Player cannot join from the banned device even with different accounts.",
        inline=False
    )

    await interaction.followup.send(
        embed=embed,
        view=PCBanView(userid, reason, data['name'], data['display'], interaction.user)
    )


@tree.command(name="unpcban", description="Remove PC ban")
@app_commands.describe(userid="Roblox UserID to unban")
async def unpcban_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"User {userid}"
    display_name = data['display'] if data else username

    embed = ZeroTwoEmbed(
        title="Confirm PC Unban",
        description=f"PC Unban **{username}**?",
        color=0xffd700,
        target_user=f"{username} ({userid})",
        moderator=interaction.user
    )

    if data and data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="⚠️ Warning", value="This will remove the device-based PC ban for this user.", inline=False)

    await interaction.followup.send(
        embed=embed,
        view=UnPCBanView(userid, username, display_name, interaction.user)
    )


@tree.command(name="banasync", description="Ban a player by userid")
@app_commands.describe(userid="The Roblox user ID to ban", reason="Reason for the ban")
async def banasync_command(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/send_command",
            json={
                "command": "ban",
                "userid": userid,
                "reason": reason,
                "executor": interaction.user.name,
                "username": username,
                "banType": "normal"
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ZeroTwoEmbed(
                title="✅ Ban Command Sent",
                description=f"**{username}** has been banned.",
                color=0x00ff00,
                target_user=f"{username} ({userid})",
                moderator=interaction.user,
                reason=reason,
                type="Normal Ban"
            )
        else:
            error_msg = response.text if response.text else f"Status: {response.status_code}"
            embed = ZeroTwoEmbed(title="❌ Ban Command Failed", description=f"Error: {error_msg}", color=0xff0000)

        await interaction.followup.send(embed=embed)

    except requests.exceptions.Timeout:
        embed = ZeroTwoEmbed(
            title="❌ Timeout Error",
            description="Request timed out. Server may be unavailable.",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Failed to send ban command: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="unbanasync", description="Unban a player by userid")
@app_commands.describe(userid="The Roblox user ID to unban")
async def unbanasync_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        data = await get_roblox_user_data(userid)
        username = data['name'] if data else f"User {userid}"

        response = requests.post(
            f"{API_URL}/send_command",
            json={
                "command": "unban",
                "userid": userid,
                "executor": interaction.user.name
            },
            timeout=10
        )

        if response.status_code == 200:
            embed = ZeroTwoEmbed(
                title="✅ Unban Command Sent",
                description=f"**{username}** has been unbanned.",
                color=0x00ff00,
                target_user=f"{username} ({userid})",
                moderator=interaction.user
            )
        else:
            error_msg = response.text if response.text else f"Status: {response.status_code}"
            embed = ZeroTwoEmbed(title="❌ Unban Command Failed", description=f"Error: {error_msg}", color=0xff0000)

        await interaction.followup.send(embed=embed)

    except requests.exceptions.Timeout:
        embed = ZeroTwoEmbed(
            title="❌ Timeout Error",
            description="Request timed out. Server may be unavailable.",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Failed to send unban command: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="banlist", description="View bans with advanced filtering")
async def banlist_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
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
                    ban['display_name'] = username

            enriched_bans.append(ban)

        view = EnhancedBanListView(enriched_bans, interaction.user)
        embed = view.get_embed()

        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        logger.error(f"Error getting banlist: {str(e)}")
        embed = ZeroTwoEmbed(title="Connection Error", description="Cannot get ban list.", color=0xff0000)
        await interaction.followup.send(embed=embed)


# ===== SERVER COMMANDS =====

@tree.command(name="warn", description="Warn a player")
@app_commands.describe(userid="Roblox UserID", reason="Warning reason")
async def warn_command(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    embed = ZeroTwoEmbed(
        title="Confirm Warning",
        description=f"Warn **{data['name']}**?",
        color=0xffd700,
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="💢 Reason", value=reason, inline=False)

    await interaction.followup.send(
        embed=embed,
        view=WarnView(userid, reason, data['name'], interaction.user)
    )


@tree.command(name="cleannotes", description="Remove all moderation notes from a player")
@app_commands.describe(userid="Roblox UserID")
async def cleannotes_command(interaction: discord.Interaction, userid: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    if not data:
        embed = ZeroTwoEmbed(title="User not found", description=f"ID `{userid}` not found on Roblox.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    embed = ZeroTwoEmbed(
        title="Confirm Clean Notes",
        description=f"Remove ALL notes for **{data['name']}**?",
        color=0xffa500,
        target_user=f"{data['name']} (@{data['display']})",
        moderator=interaction.user
    )

    if data['avatar']:
        embed.set_thumbnail(url=data['avatar'])

    embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)
    embed.add_field(name="⚠️ Warning", value="This action cannot be undone! All notes will be permanently deleted.", inline=False)

    await interaction.followup.send(
        embed=embed,
        view=CleanNotesView(userid, data['name'], data['display'], interaction.user)
    )


@tree.command(name="players", description="Show detailed online player list")
async def players_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        res = requests.get(f"{API_URL}/get_players", timeout=10)
        res.raise_for_status()
        data = res.json()
        count = data.get('count', 0)
        players = data.get('players', [])

        embed = ZeroTwoEmbed(
            title="🎮 Online Players",
            description=f"Total online: **{count}**",
            color=0x0000ff
        )

        if not players:
            embed.description = f"Total online: **{count}**\n\n*No player details available.*"
        else:
            for i, p in enumerate(players[:25], 1):
                userid = p.get('userid', 'Unknown')
                username = p.get('username', 'Unknown')
                display = p.get('display', username)
                playtime = p.get('playtime', 0)

                is_banned = False
                try:
                    bans_res = requests.get(f"{API_URL}/get_bans", timeout=2)
                    if bans_res.status_code == 200:
                        bans = bans_res.json()
                        for ban in bans:
                            if str(ban.get('userid')) == str(userid):
                                is_banned = True
                                break
                except:
                    pass

                user_display = f"{username} (@{display})" if display != username else username
                status = "🔴 BANNED" if is_banned else "🟢 ONLINE"

                embed.add_field(
                    name=f"{i}. {user_display}",
                    value=f"ID: `{userid}`\nStatus: {status}\nPlaytime: `{playtime}m`",
                    inline=True
                )

        await interaction.edit_original_response(embed=embed)

    except Exception as e:
        logger.error(f"Failed to fetch player list: {str(e)}")
        await interaction.edit_original_response(content="❌ Failed to fetch player list.")


@tree.command(name="find", description="Find player by username")
@app_commands.describe(username="Username to search for")
async def find_command(interaction: discord.Interaction, username: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        response = requests.get(f"{API_URL}/get_players", timeout=10)
        if response.status_code == 200:
            players_data = response.json()
            players = players_data.get('players', [])

            matching_players = []
            for player in players:
                if username.lower() in player.get('username', '').lower():
                    matching_players.append(player)

            embed = ZeroTwoEmbed(
                title="Player Search",
                description=f"Searching for '{username}'",
                color=0x0000ff
            )

            if matching_players:
                player_list = ""
                for i, player in enumerate(matching_players[:10], 1):
                    player_list += f"{i}. **{player.get('username', 'Unknown')}** (ID: `{player.get('userid', 'Unknown')}`)\n"

                if len(matching_players) > 10:
                    player_list += f"\n... and {len(matching_players)-10} more"

                embed.add_field(name="Matches Found", value=player_list, inline=False)
            else:
                embed.add_field(name="No Matches", value="No players found with that username.", inline=False)

            await interaction.followup.send(embed=embed)
        else:
            embed = ZeroTwoEmbed(title="Error", description="Cannot search for players.", color=0xff0000)
            await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ZeroTwoEmbed(title="Error", description=f"Search failed: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="lookup", description="Check player moderation history")
@app_commands.describe(userid="Roblox UserID")
async def lookup_command(interaction: discord.Interaction, userid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not userid.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="UserID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    data = await get_roblox_user_data(userid)
    username = data['name'] if data else f"ID: {userid}"

    try:
        bans_res = requests.get(f"{API_URL}/get_bans", timeout=10)
        is_banned = False
        ban_reason = ""
        ban_type = "normal"
        ban_date = ""

        if bans_res.status_code == 200:
            bans = bans_res.json()
            for ban in bans:
                if str(ban.get('userid')) == userid:
                    is_banned = True
                    ban_reason = ban.get('reason', 'No reason')
                    ban_type = ban.get('banType', 'normal')
                    if ban.get('timestamp'):
                        ban_date = datetime.fromtimestamp(ban['timestamp']).strftime('%Y-%m-%d %H:%M')
                    break

        notes_res = requests.get(f"{API_URL}/get_notes?userid={userid}", timeout=5)
        notes = []
        if notes_res.status_code == 200:
            notes = notes_res.json()

        linked_count = 0
        suspicious_score = 0

        try:
            check_res = requests.post(
                f"{API_URL}/send_command",
                json={"command": "check_suspicious", "userid": userid},
                timeout=5
            )
            if check_res.status_code == 200:
                check_data = check_res.json()
                linked_count = len(check_data.get('linkedAccounts', []))
                suspicious_score = check_data.get('suspiciousScore', 0)
        except:
            pass

        embed = ZeroTwoEmbed(
            title="Player Lookup",
            description=f"Information for **{username}**",
            color=0x0000ff
        )

        if data:
            if data['avatar']:
                embed.set_thumbnail(url=data['avatar'])
            embed.add_field(name="👤 Roblox Username", value=data['name'], inline=True)
            embed.add_field(name="✨ Display Name", value=data['display'], inline=True)

        embed.add_field(name="🆔 UserID", value=f"`{userid}`", inline=True)

        if is_banned:
            ban_status = "Banned"
            if ban_type == "pc":
                ban_status = "PC Banned"
            embed.add_field(name="🚫 Ban Status", value=ban_status, inline=True)
            embed.add_field(name="💢 Ban Reason", value=ban_reason, inline=False)
            embed.add_field(name="🔰 Ban Type", value="PC Ban" if ban_type == "pc" else "Normal Ban", inline=True)
            if ban_date:
                embed.add_field(name="📆 Ban Date", value=ban_date, inline=True)
        else:
            embed.add_field(name="🚫 Ban Status", value="✅ Not banned", inline=True)

        if notes:
            note_text = "\n".join([f"• {n.get('note', '')}" for n in notes[:3]])
            if len(notes) > 3:
                note_text += f"\n... and {len(notes)-3} more"
            embed.add_field(name="📝 Notes", value=note_text, inline=False)

        if linked_count > 0:
            embed.add_field(name="🔗 Linked Accounts", value=str(linked_count), inline=True)

        if suspicious_score > 0:
            embed.add_field(name="⚠️ Suspicious Score", value=str(suspicious_score), inline=True)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ZeroTwoEmbed(title="Error", description=f"Cannot lookup player: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="stats", description="Server statistics")
async def stats_command(interaction: discord.Interaction):
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

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
        permanent_bans = 0
        temporary_bans = 0

        if bans_res.status_code == 200:
            bans = bans_res.json()
            ban_count = len(bans)

            for ban in bans:
                ban_type = ban.get('banType', 'normal')
                if ban_type == 'pc':
                    pc_bans += 1
                else:
                    normal_bans += 1

                duration = ban.get('duration', -1)
                if duration == -1:
                    permanent_bans += 1
                else:
                    temporary_bans += 1

        blacklist_count = len(asset_blacklist.get_all_assets())

        suspicious_count = 0
        try:
            sus_res = requests.get(f"{API_URL}/get_suspicious_accounts", timeout=5)
            if sus_res.status_code == 200:
                sus_data = sus_res.json()
                suspicious_count = len(sus_data.get('suspiciousAccounts', []))
        except:
            pass

        embed = ZeroTwoEmbed(
            title="Server Statistics",
            description="Zero Two's Server Stats",
            color=0x800080
        )

        embed.add_field(name="👥 Online Players", value=str(player_count), inline=True)
        embed.add_field(name="🚫 Total Bans", value=str(ban_count), inline=True)
        embed.add_field(name="🔨 Normal Bans", value=str(normal_bans), inline=True)
        embed.add_field(name="💻 PC Bans", value=str(pc_bans), inline=True)
        embed.add_field(name="⏰ Permanent", value=str(permanent_bans), inline=True)
        embed.add_field(name="⏳ Temporary", value=str(temporary_bans), inline=True)
        embed.add_field(name="📦 Blacklisted", value=str(blacklist_count), inline=True)
        embed.add_field(name="⚠️ Suspicious", value=str(suspicious_count), inline=True)
        embed.add_field(name="💫 API Status", value="✅ Online", inline=True)
        embed.add_field(name="🔰 Version", value="v8.0.0", inline=True)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ZeroTwoEmbed(title="Error", description=f"Cannot get statistics: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="check", description="Check server status")
async def check_command(interaction: discord.Interaction):
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    try:
        res = requests.get(f"{API_URL}/get_players", timeout=5)
        res.raise_for_status()
        data = res.json()
        count = data.get('count', 0)
        players = data.get('players', [])

        if count == 0:
            embed = ZeroTwoEmbed(title="🌙 Server Empty", description="No players online.", color=0x808080)
        elif count < 10:
            embed = ZeroTwoEmbed(
                title="🟢 Server Online",
                description=f"{count} player{'s' if count != 1 else ''} online.",
                color=0x00ff00
            )
        elif count < 30:
            embed = ZeroTwoEmbed(
                title="🟡 Server Busy",
                description=f"{count} players online.",
                color=0xffd700
            )
        else:
            embed = ZeroTwoEmbed(
                title="🔴 Server Full",
                description=f"{count} players online.",
                color=0xff0000
            )

        if players and len(players) > 0:
            player_list = "\n".join([f"• {p.get('username', 'Unknown')}" for p in players[:5]])
            if len(players) > 5:
                player_list += f"\n... and {len(players)-5} more"
            embed.add_field(name="👥 Players", value=player_list, inline=False)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = ZeroTwoEmbed(title="Server Error", description="Cannot connect to server.", color=0xff0000)
        await interaction.response.send_message(embed=embed)


# ===== ASSET MANAGEMENT COMMANDS =====

@tree.command(name="blacklist", description="Add asset to blacklist")
@app_commands.describe(asset_id="Asset ID to blacklist")
async def blacklist_command(interaction: discord.Interaction, asset_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not asset_id.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="Asset ID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    try:
        if asset_blacklist.is_blacklisted(asset_id):
            embed = ZeroTwoEmbed(
                title="Already Blacklisted",
                description=f"Asset `{asset_id}` is already blacklisted.",
                color=0xffa500
            )
        else:
            if asset_blacklist.add_asset(asset_id):
                embed = ZeroTwoEmbed(
                    title="✅ Asset Blacklisted",
                    description=f"Asset `{asset_id}` has been added to blacklist.",
                    color=0x00ff00
                )
            else:
                embed = ZeroTwoEmbed(
                    title="❌ Failed",
                    description=f"Failed to blacklist asset `{asset_id}`.",
                    color=0xff0000
                )
    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Error: {str(e)}", color=0xff0000)

    await interaction.followup.send(embed=embed)


@tree.command(name="unblacklist", description="Remove asset from blacklist")
@app_commands.describe(asset_id="Asset ID to remove from blacklist")
async def unblacklist_command(interaction: discord.Interaction, asset_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not asset_id.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="Asset ID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    try:
        if not asset_blacklist.is_blacklisted(asset_id):
            embed = ZeroTwoEmbed(
                title="Not Blacklisted",
                description=f"Asset `{asset_id}` is not in blacklist.",
                color=0xffa500
            )
        else:
            if asset_blacklist.remove_asset(asset_id):
                embed = ZeroTwoEmbed(
                    title="✅ Asset Removed",
                    description=f"Asset `{asset_id}` has been removed from blacklist.",
                    color=0x00ff00
                )
            else:
                embed = ZeroTwoEmbed(
                    title="❌ Failed",
                    description=f"Failed to remove asset `{asset_id}`.",
                    color=0xff0000
                )
    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Error: {str(e)}", color=0xff0000)

    await interaction.followup.send(embed=embed)


@tree.command(name="viewblacklist", description="View all blacklisted assets")
async def viewblacklist_command(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        assets = asset_blacklist.get_all_assets()

        embed = ZeroTwoEmbed(
            title="Asset Blacklist",
            description="List of blacklisted assets",
            color=0x800080
        )

        if assets:
            embed.add_field(name="Total Assets", value=str(len(assets)), inline=True)

            asset_list = "\n".join([f"`{asset}`" for asset in assets[:10]])
            embed.add_field(name="Assets", value=asset_list if asset_list else "None", inline=False)

            if len(assets) > 10:
                embed.set_footer(text=f"And {len(assets)-10} more assets... • Zero Two")
        else:
            embed.add_field(name="Blacklist", value="No assets are currently blacklisted.", inline=False)

        await interaction.followup.send(embed=embed)
    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Error: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


@tree.command(name="checkasset", description="Check if asset is blacklisted")
@app_commands.describe(asset_id="Asset ID to check")
async def checkasset_command(interaction: discord.Interaction, asset_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("No permission, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    if not asset_id.isdigit():
        embed = ZeroTwoEmbed(title="Invalid ID", description="Asset ID must be numbers only.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    try:
        is_blacklisted = asset_blacklist.is_blacklisted(asset_id)

        if is_blacklisted:
            embed = ZeroTwoEmbed(
                title="🔴 Blacklisted",
                description=f"Asset `{asset_id}` is blacklisted.",
                color=0xff0000
            )
        else:
            embed = ZeroTwoEmbed(
                title="🟢 Allowed",
                description=f"Asset `{asset_id}` is not blacklisted.",
                color=0x00ff00
            )
    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Error: {str(e)}", color=0xff0000)

    await interaction.followup.send(embed=embed)


@tree.command(name="clearblacklist", description="Clear all blacklisted assets (Admin)")
async def clearblacklist_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        assets = asset_blacklist.get_all_assets()
        count = len(assets)

        if count == 0:
            embed = ZeroTwoEmbed(title="Blacklist Empty", description="No assets to clear.", color=0xffa500)
            await interaction.followup.send(embed=embed)
        else:
            embed = ZeroTwoEmbed(
                title="Confirm Clear Blacklist",
                description=f"This will clear ALL {count} blacklisted assets.",
                color=0xff0000,
                moderator=interaction.user
            )
            embed.add_field(name="⚠️ Warning", value="This action cannot be undone!", inline=False)

            await interaction.followup.send(
                embed=embed,
                view=ClearBlacklistView(count, interaction.user)
            )

    except Exception as e:
        embed = ZeroTwoEmbed(title="❌ Error", description=f"Error: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


# ===== ADMIN COMMANDS =====

@tree.command(name="restart", description="Restart server (Admin)")
async def restart_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    embed = ZeroTwoEmbed(
        title="Restart Server",
        description="Restart the game server?",
        color=0xffa500,
        moderator=interaction.user
    )
    embed.add_field(name="⚠️ Warning", value="All players will be disconnected.", inline=False)

    view = ConfirmActionView("restart", "", "", "", interaction.user, is_admin=True)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="shutdown", description="Shutdown server (Admin)")
async def shutdown_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    embed = ZeroTwoEmbed(
        title="Shutdown Server",
        description="Shutdown the game server?",
        color=0xff0000,
        moderator=interaction.user
    )
    embed.add_field(name="⚠️ Warning", value="Server will stop completely.", inline=False)

    view = ConfirmActionView("shutdown", "", "", "", interaction.user, is_admin=True)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="announce", description="Send announcement to server")
@app_commands.describe(message="Announcement message")
async def announce_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    embed = ZeroTwoEmbed(
        title="Announcement Confirmation",
        description="Send this announcement to all players?",
        color=0xffd700,
        moderator=interaction.user
    )
    embed.add_field(name="📝 Message", value=message, inline=False)

    await interaction.response.send_message(
        embed=embed,
        view=AnnounceView(message, interaction.user)
    )


@tree.command(name="broadcast", description="Broadcast message to all players")
@app_commands.describe(message="Broadcast message")
async def broadcast_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    embed = ZeroTwoEmbed(
        title="Broadcast Confirmation",
        description="Send this broadcast to all players?",
        color=0x0000ff,
        moderator=interaction.user
    )
    embed.add_field(name="📝 Message", value=message, inline=False)

    await interaction.response.send_message(
        embed=embed,
        view=BroadcastView(message, interaction.user)
    )


@tree.command(name="logs", description="View server logs")
@app_commands.describe(lines="Number of log lines (default: 10)")
async def logs_command(interaction: discord.Interaction, lines: int = 10):
    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        logs_res = requests.get(f"{API_URL}/get_logs?lines={lines}", timeout=10)

        embed = ZeroTwoEmbed(
            title="Server Logs",
            description="Recent server activity",
            color=0x808080
        )

        if logs_res.status_code == 200:
            logs_data = logs_res.json()
            logs = logs_data.get('logs', [])

            if logs:
                log_text = ""
                for i, log in enumerate(logs[:lines], 1):
                    log_text += f"{i:2d}. {log}\n"

                if len(log_text) > 1000:
                    log_text = log_text[:997] + "..."

                embed.add_field(name=f"Last {len(logs)} entries:", value=f"```\n{log_text}\n```", inline=False)
            else:
                embed.add_field(name="No logs", value="No log entries available.", inline=False)
        else:
            embed.add_field(
                name="Logs unavailable",
                value="Log API endpoint not available.\nCheck API server configuration.",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = ZeroTwoEmbed(title="Error", description=f"Cannot get logs: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed)


# ===== SYSTEM COMMANDS =====

@tree.command(name="settings", description="Manage system settings")
@app_commands.describe(
    onjoin="Enable/Disable on-join checks (True/False)", 
    onlog="Enable/Disable logging (True/False)", 
    banasync="Enable/Disable anti-cheat auto-ban (True/False)"
)
async def settings_command(
    interaction: discord.Interaction,
    onjoin: Optional[str] = None,
    onlog: Optional[str] = None,
    banasync: Optional[str] = None
):
    def to_bool(val):
        if val is None:
            return None
        return val.lower() in ['true', 'yes', '1', 'on']

    onjoin_bool = to_bool(onjoin)
    onlog_bool = to_bool(onlog)
    banasync_bool = to_bool(banasync)

    if not is_admin(interaction):
        await interaction.response.send_message("Admin only, DARLING~", ephemeral=True)
        return

    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    update_data = {}
    if onjoin_bool is not None:
        update_data["onjoin"] = onjoin_bool
    if onlog_bool is not None:
        update_data["onlog"] = onlog_bool
    if banasync_bool is not None:
        update_data["banasync"] = banasync_bool

    try:
        if update_data:
            res = requests.post(f"{API_URL}/update_settings", json=update_data, timeout=5)
            msg = "✅ Settings updated."
        else:
            res = requests.get(f"{API_URL}/get_settings", timeout=5)
            msg = "⚙️ Current Settings:"

        if res.status_code == 200:
            curr_settings = res.json().get("settings", res.json())
            embed = ZeroTwoEmbed(
                title="System Settings",
                description=msg,
                color=0x0000ff,
                moderator=interaction.user
            )
            for k, v in curr_settings.items():
                embed.add_field(name=k.capitalize(), value="✅ Enabled" if v else "❌ Disabled", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to manage settings.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")


@tree.command(name="client_fix", description="Send a client-side fix (Reset, Fix Camera)")
@app_commands.describe(type="Fix type (reset/camera)")
@app_commands.choices(type=[
    app_commands.Choice(name="Server Reset", value="reset"),
    app_commands.Choice(name="Fix Camera", value="camera")
])
async def client_fix_command(interaction: discord.Interaction, type: str):
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    try:
        res = requests.post(f"{API_URL}/client_fix", json={"type": type}, timeout=5)
        if res.status_code == 200:
            await interaction.response.send_message(f"✅ Client fix `{type}` sent to server, DARLING~")
        else:
            await interaction.response.send_message("❌ Failed to send client fix.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")


@tree.command(name="ping", description="Check bot status")
async def ping_command(interaction: discord.Interaction):
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    latency = round(bot.latency * 1000, 2)
    api_status = check_api()

    api_time = None
    if api_status:
        start = time.time()
        requests.get(f"{API_URL}/get_players", timeout=5)
        api_time = round((time.time() - start) * 1000, 2)

    if latency < 100:
        color = 0xff69b4
        mood = "⚡ Zero Two: DARLING is so fast! ⚡"
    elif latency < 200:
        color = 0xff1493
        mood = "💕 Zero Two: Perfect as always, DARLING~ 💕"
    elif latency < 300:
        color = 0xdb7093
        mood = "😊 Zero Two: Not bad, my DARLING 😊"
    elif latency < 500:
        color = 0xc71585
        mood = "😴 Zero Two: DARLING is sleepy... 😴"
    else:
        color = 0x8b0000
        mood = "💢 Zero Two: DARLING! So slow! 💢"

    embed = ZeroTwoEmbed(
        title="ZERO TWO STATUS",
        description=f"Code:002 - Partner Kynx",
        color=color
    )

    embed.add_field(name="📡 Discord Latency", value=f"```{latency}ms```", inline=True)
    embed.add_field(name="💫 API Connection", value="✨ ONLINE ✨" if api_status else "💔 OFFLINE 💔", inline=True)
    if api_time:
        embed.add_field(name="⏱️ API Response", value=f"```{api_time}ms```", inline=True)
    embed.add_field(name="🔰 Version", value="```v8.0.0```", inline=True)
    embed.add_field(name="💬 Zero Two Says:", value=f"*{mood}*", inline=False)

    embed.add_field(name="📊 Commands Used", value=f"```{sum(command_stats.values())}```", inline=True)
    embed.add_field(name="🕒 Uptime", value=f"```{timedelta(seconds=int(time.time() - bot.start_time))}```" if hasattr(bot, 'start_time') else "```Unknown```", inline=True)

    await interaction.response.send_message(embed=embed)


@tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    embed = ZeroTwoEmbed(
        title="Zero Two's Commands Help",
        description="Game server moderation bot - Full command list",
        color=0xff69b4
    )

    embed.add_field(
        name="**👤 Player Management**",
        value="""`/kick [id] [reason]` - Kick player
`/mute [id] [duration] [reason]` - Mute player
`/umute [id]` - Unmute player
`/userlogs [id] [limit]` - View user logs
`/addnote [id] [note]` - Add note to player
`/userinfo [id]` - Get user info
`/gameinfo [placeid]` - Get game info""",
        inline=False
    )

    embed.add_field(
        name="**🔨 Ban Commands**",
        value="""`/ban [id] [reason] [duration] [type] [ban_linked]` - Ban player
`/unban [id] [type]` - Unban player
`/pcban [id] [reason]` - PC Ban player
`/unpcban [id]` - Remove PC ban
`/banasync [id] [reason]` - Async ban
`/unbanasync [id]` - Async unban
`/banlist` - View all bans (with filters)""",
        inline=False
    )

    embed.add_field(
        name="**💫 Server Commands**",
        value="""`/warn [id] [reason]` - Warn player
`/cleannotes [id]` - Remove all notes (Admin)
`/players` - Online players list
`/find [name]` - Find player
`/lookup [id]` - Player history
`/stats` - Server statistics
`/check` - Server status""",
        inline=False
    )

    embed.add_field(
        name="**📦 Asset Management**",
        value="""`/blacklist [id]` - Block asset
`/unblacklist [id]` - Unblock asset
`/viewblacklist` - List blocked assets
`/checkasset [id]` - Check asset
`/clearblacklist` - Clear all (Admin)""",
        inline=False
    )

    embed.add_field(
        name="**⚡ Admin Commands**",
        value="""`/restart` - Restart server
`/shutdown` - Stop server
`/announce [msg]` - Announcement
`/broadcast [msg]` - Broadcast
`/logs [lines]` - View server logs""",
        inline=False
    )

    embed.add_field(
        name="**🔧 System & Client**",
        value="""`/settings [onjoin] [onlog] [banasync]` - System toggles
`/client_fix [type]` - Reset/Camera fix""",
        inline=False
    )

    embed.add_field(
        name="**📡 Utility**",
        value="""`/ping` - Bot status
`/help` - This menu
`/cmds` - Quick commands""",
        inline=False
    )

    embed.set_footer(text="Zero Two • Code:002 • Total commands: 37 • DARLING~")
    await interaction.response.send_message(embed=embed)


@tree.command(name="cmds", description="Show all commands (short version)")
async def cmds_command(interaction: discord.Interaction):
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message("Rate limited! Slow down, DARLING~", ephemeral=True)
        return

    commands_list = """**Zero Two's Quick Commands List:**

**Player Management:**
`/mute`, `/umute`, `/kick`, `/userlogs`, `/addnote`, `/userinfo`, `/gameinfo`

**Ban Commands:**
`/ban`, `/unban`, `/pcban`, `/unpcban`, `/banasync`, `/unbanasync`, `/banlist`

**Server Commands:**
`/warn`, `/cleannotes`, `/players`, `/find`, `/lookup`, `/stats`, `/check`

**Asset Management:**
`/blacklist`, `/unblacklist`, `/viewblacklist`, `/checkasset`, `/clearblacklist`

**Admin:**
`/restart`, `/shutdown`, `/announce`, `/broadcast`, `/logs`

**System & Client:**
`/settings`, `/client_fix`

**Utility:**
`/ping`, `/help`, `/cmds`"""

    embed = ZeroTwoEmbed(
        title="Zero Two's Quick Commands",
        description=commands_list,
        color=0xff69b4
    )
    embed.set_footer(text="Use /help for detailed information • Total: 37 commands • Code:002")
    await interaction.response.send_message(embed=embed)


# ===== BOT EVENTS =====
@bot.event
async def on_ready():
    bot.start_time = time.time()
    logger.info(f"Zero Two ready: {bot.user}")

    sync_blacklist.start()
    update_cache.start()
    cleanup_temp_files.start()

    try:
        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} global commands")

        command_names = [cmd.name for cmd in synced]
        logger.info(f"Synced commands: {', '.join(command_names)}")
        logger.info("Zero Two Bot v8.0.0 is now online! DARLING~")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No permission, DARLING~", ephemeral=True)
    else:
        logger.error(f"Error: {str(error)}")
        await ctx.send("❌ Error, DARLING~", ephemeral=True)


# ===== MAIN FUNCTION =====
def run():
    if TOKEN:
        logger.info("Starting Zero Two Bot v8.0.0...")
        logger.info("Code:002 - DARLING is here!")
        logger.info(f"Total commands loaded: 37")
        logger.info("Version: v8.0.0")
        logger.info("Anti-Ban Protection: ✅ Enabled")
        logger.info("Encrypted Storage: ✅ Active")
        logger.info("Mute/Umute commands: ✅ Fixed & Restored")
        logger.info("PC Ban system: ✅ Enabled")
        logger.info(f"Banlist Auto-save: ✅ ALWAYS enabled (saves to {BANLIST_DIR}/)")
        logger.info("Asset Blacklist: ✅ Integrated with API")
        logger.info("Caching System: ✅ Enabled")
        logger.info("Rate Limiting: ✅ Active")
        bot.run(TOKEN)
    else:
        logger.error("No token found in .env file")


if __name__ == "__main__":
    run()