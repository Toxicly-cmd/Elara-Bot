from __future__ import annotations
import discord
from discord.ext import commands
import inspect
import datetime
import traceback
import sys
import asyncio
import time
import importlib
from collections import defaultdict

from Elara.config import config
BotConfig = config.BotConfigClass()
from Elara.memory.cache import cache
from Elara.style import color, emoji, urls
from Elara.console.logging import logger
from storage import guilds_log as guilds_log_db
import storage

def get_function_args(func):
    signature = inspect.signature(func)
    return [param.name for param in signature.parameters.values()]

class Log:
    def __init__(self, bot):
        self.bot = bot
        self.log_error_type = [type for type in get_function_args(guilds_log_db.get) if type not in ['guild_id', 'id', 'enabled', 'updated_at', 'created_at']]
        self.timeout_data = defaultdict(lambda: {"count": 0, "last_log_time": 0, "queue": None})
    
    async def send(self, guild: discord.Guild, type: str, embed: discord.Embed = None, content: str = None):
        type = type.lower() + "_channel_id"
        guilds_log_cache = cache.guilds_log.get(str(guild.id))
        if not guilds_log_cache or not guilds_log_cache.get('enabled'): return
        if type not in self.log_error_type: return
        channel_id = guilds_log_cache.get(type)
        if not channel_id: return
        channel = guild.get_channel(int(channel_id))
        if not channel or (not embed and not content): return
        if not embed: embed = discord.Embed(title="Error", description=content, color=color.red)
        guild_data = self.timeout_data[guild.id]
        if guild_data["queue"] is None:
            guild_data["queue"] = asyncio.Queue()
            asyncio.create_task(self.process_queue(guild))
        await guild_data["queue"].put((channel, embed))
    
    async def process_queue(self, guild: discord.Guild):
        guild_data = self.timeout_data[guild.id]
        queue = guild_data["queue"]
        while True:
            channel, embed = await queue.get()
            current_time = time.time()
            if current_time - guild_data["last_log_time"] > 60: guild_data["count"] = 0
            if guild_data["count"] >= 20: await asyncio.sleep(5)
            try:
                await channel.send(embed=embed)
                guild_data["count"] += 1
                guild_data["last_log_time"] = current_time
            except Exception as e: logger.error(f"Error in Log.process_queue: {e}")

class antinuke_log:
    def __init__(self, bot):
        self.bot = bot
        self.log_error_type = [type for type in get_function_args(guilds_log_db.get) if type not in ['guild_id','id','enabled','updated_at','created_at']]
    async def send(self,guild:discord.Guild,type:str,embed:discord.Embed=None,content:str=None):
        type = type.lower()+ "_channel_id"
        try:
            guilds_log_cache = cache.guilds_log[str(guild.id)]
            if not guilds_log_cache.get('enabled'): return
            channel_id = guilds_log_cache.get(type)
            if not channel_id: return
            channel = guild.get_channel(int(channel_id))
            if not channel: return
            if embed: await channel.send(embed=embed)
            elif content: await channel.send(content=content)
        except: pass

class AutoShardedBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix="=", # This is a placeholder, get_prefix handles the real logic
            case_insensitive=True,
            intents=discord.Intents.all(),
            status=discord.Status.dnd,
            strip_after_prefix=True,
            help_command=None,
            shard_count=BotConfig.SHARD_COUNT,
            allowed_mentions=discord.AllowedMentions(everyone=False, replied_user=False, roles=False)
        )
        self.log = Log(self)
        self.antinuke_log = antinuke_log(self)
        self.users_data = config.users
        self.channels = config.channels
        self.BotConfig = BotConfig
        self.urls = urls
        self.emoji = emoji
        self.cache = cache
        self.storage = storage
        self.database = self.storage
        self.VERSION = '1.0.0'
        self.start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        self.developers = []
        self.variables = {
            "{user}": "The user's name",
            "{user.id}": "The user's id",
            "{user.mention}": "The user's mention",
            "{guild}": "The server name",
            "{server}": "The server name",
            "{server.id}": "The server id",
            "{member.count}": "The server member count"
        }
        self.add_check(self._check_command_access)

    async def _check_command_access(self, ctx: commands.Context) -> bool:
        if not ctx.guild or not ctx.command: return True
        from Elara.src.checks.checks import check_is_admin_predicate, check_is_owner_raw
        if check_is_admin_predicate(ctx.author) or await check_is_owner_raw(ctx.author, ctx.guild): return True
        command_access = cache.command_access.get(str(ctx.guild.id), {})
        disabled_commands = set(command_access.get("disabled_commands", []) or [])
        qualified_name = getattr(ctx.command, "qualified_name", ctx.command.name)
        if any(name in disabled_commands for name in [qualified_name] + qualified_name.split()[:-1]):
            raise commands.CheckFailure("This command is disabled in this server.")
        return True

    async def get_prefix(self, message: discord.Message):
        default_prefix = str(BotConfig.PREFIX)
        if not message.guild: return commands.when_mentioned_or(default_prefix)(self, message)
        user_id_str = str(message.author.id)
        user_cache = cache.users.get(user_id_str, {})
        is_dev = message.author.id in self.users_data.developer
        has_npr = is_dev or user_cache.get('no_prefix', False) or user_cache.get('no_prefix_subscription', False)
        if has_npr and not is_dev:
            no_prefix_end = user_cache.get('no_prefix_end')
            if no_prefix_end:
                try:
                    expire_at = datetime.datetime.fromisoformat(no_prefix_end) if isinstance(no_prefix_end, str) else no_prefix_end
                    if expire_at.astimezone() < datetime.datetime.now().astimezone(): has_npr = False
                except: pass
        prefix = cache.guilds.get(str(message.guild.id), {}).get('prefix', default_prefix)
        if has_npr: return commands.when_mentioned_or(prefix, '')(self, message)
        return commands.when_mentioned_or(prefix)(self, message)

    async def on_message(self, message):
        pass

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure, commands.CommandOnCooldown, commands.MissingRequiredArgument)): return
        logger.error(f"Command Error: {ctx.command} - {ctx.author}: {error}")

    async def on_error(self, event_method, *args, **kwargs):
        logger.error(f"Event Error in {event_method}: {traceback.format_exc()}")
