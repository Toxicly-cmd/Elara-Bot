from __future__ import annotations
import discord


from discord.ext import commands


import datetime


import traceback, sys


import json


import Elara.src.checks.checks as checks


from Elara.memory.cache import cache


import storage.antinuke_bypass


import storage.antinuke_settings


import storage.guilds


import storage.guilds_backup


from Elara.console.logging import logger


from Elara.style import color


from Elara.utils import pings


import asyncio


from Elara.config.config import BotConfigClass


BotConfig = BotConfigClass()


from Elara.engine.Bot import AutoShardedBot


import storage


async def backup_guild(guild_id: int, bot: AutoShardedBot):

    try:

        guild = bot.get_guild(guild_id)

        if guild is None:

            return logger.error(f"Guild {guild_id} not found")

        data = {
            "channels": [],
            "roles": [],
            "users": [],
            "guild": {
                "name": guild.name,
            },
        }

        for channel in guild.channels:

            channel_data = {
                "name": channel.name,
                "category": channel.category.name if channel.category else None,
                "type": str(channel.type),
                "position": channel.position,
                "nsfw": channel.is_nsfw(),
                "slowmode": (
                    channel.slowmode_delay
                    if channel.type == discord.ChannelType.text
                    else None
                ),
                "topic": (
                    channel.topic if channel.type == discord.ChannelType.text else None
                ),
                "overwrites": {
                    "everyone": channel.overwrites_for(guild.default_role)
                    .pair()[0]
                    .value
                },
                "members_overwrites": {},
            }

            for channel_overwrite in channel.overwrites:

                #  if its @everyone, skip it

                if (
                    isinstance(channel_overwrite, discord.Role)
                    and channel_overwrite != guild.default_role
                ):

                    channel_data["overwrites"][str(channel_overwrite.name)] = (
                        channel.overwrites_for(channel_overwrite).pair()[0].value
                    )

                elif isinstance(channel_overwrite, discord.Member):

                    channel_data["members_overwrites"][str(channel_overwrite.id)] = (
                        channel.overwrites_for(channel_overwrite).pair()[0].value
                    )

            data["channels"].append(channel_data)

        for role in guild.roles:

            # if the role is bot role, skip it

            if role.is_bot_managed():

                continue

            role_data = {
                "name": role.name,
                "position": role.position,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable,
                "permissions": role.permissions.value,
            }

            data["roles"].append(role_data)

        for member in guild.members:

            member_data = {
                "id": member.id,
                "roles": [role.name for role in member.roles],
                "nick": member.nick,
            }

            data["users"].append(member_data)

        await storage.guilds_backup.insert(guild_id=guild_id, backup=data)

    except Exception as e:

        logger.error(
            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
        )


class Backup(commands.Cog):

    def __init__(self, bot: AutoShardedBot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Backup"

            category = "Main"

            description = "Backup the server"

            hidden = False

            emoji = bot.emoji.BACKUP

        self.cog_info = cog_info

    async def send_denied_embed(self, ctx: commands.Context, message: str, delete_after: int = 10):
        embed = discord.Embed(
            description=f"{self.bot.emoji.ERROR} {message}",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.bot.user.display_avatar.url)
        return await ctx.send(embed=embed, delete_after=delete_after)

    async def send_success_embed(self, ctx: commands.Context, message: str, delete_after: int = None):
        embed = discord.Embed(
            description=f"{self.bot.emoji.SUCCESS} {message}",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.bot.user.display_avatar.url)
        return await ctx.send(embed=embed, delete_after=delete_after)

    @commands.group(
        name="backup",
        description="Backup the server",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def backup(self, ctx):

        if ctx.author.id != ctx.guild.owner.id:

            return await self.send_denied_embed(ctx, "You must be the owner of the server to use this command")

        embed = discord.Embed(
            description=f"**Server Backup** {self.bot.emoji.BACKUP}\nProtect and restore your server configuration.\n\n**__Commands:__**\n",
            color=0x2b2d31
        )
        
        formatted_cmds = []
        if hasattr(ctx.command, "commands"):
            for command in ctx.command.commands:
                formatted_cmds.append(f"> `{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.description}")
        
        embed.description += "\n".join(formatted_cmds) if formatted_cmds else "No commands available."
        
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @backup.command(name="create", description="Create a backup of the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def create(self, ctx):

        try:

            if ctx.author.id != ctx.guild.owner.id:

                return await self.send_denied_embed(ctx, "You must be the owner of the server to use this command")

            await backup_guild(ctx.guild.id, self.bot)

            await self.send_success_embed(ctx, "Backup created successfully")

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await self.send_denied_embed(ctx, "An error occurred while creating the backup")


async def setup(bot):
    await bot.add_cog(Backup(bot))
