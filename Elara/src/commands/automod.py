from __future__ import annotations
import discord


from discord.ext import commands


import datetime


import traceback, sys


import Elara.src.checks.checks as checks


from Elara.memory.cache import cache


import storage.antinuke_bypass


import storage.antinuke_settings


import storage.automod


from Elara.console.logging import logger


from Elara.style import color


from Elara.utils import pings


import asyncio


from Elara.config.config import BotConfigClass


BotConfig = BotConfigClass()


import json


from Elara.engine.Bot import AutoShardedBot


import storage


class Automod(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Automod"

            category = "Main"

            description = "Automod system"

            hidden = False

            emoji = self.bot.emoji.AUTOMOD

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

    @commands.hybrid_group(
        name="automod",
        help="Enable/Disable AutoMod system or edit settings",
        with_app_command=True,
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def automod_command(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="Automod",
                color=0x2b2d31
            )
            
            formatted_cmds = []
            if hasattr(ctx.command, "commands"):
                for command in ctx.command.commands:
                    formatted_cmds.append(f"`{ctx.command.name} {command.name}`")
            
            embed.description = "**__Automod__**\n"
            embed.description += " , ".join(formatted_cmds) if formatted_cmds else "No commands available."
            
            embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @automod_command.command(
        name="enable", help="Enable AutoMod system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def automod_command_enable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if (
                Automod_Cache.get("antilink_enabled", False)
                and Automod_Cache.get("antispam_enabled", False)
                and Automod_Cache.get("antibadwords_enabled", False)
            ):

                return await self.send_denied_embed(ctx, "AutoMod is already enabled")

                return

            antilink_enabled = Automod_Cache.get("antilink_enabled", False)

            antibadwords_enabled = Automod_Cache.get("antibadwords_enabled", False)

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Engaging AutoMod shields...",
                    color=0x2b2d31
                )
            )

            try:

                antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                if antilink_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        await rule.edit(enabled=True)

                        antilink_enabled = True

                    except:

                        pass

            except:

                pass

            try:

                antibadwords_rule_id = Automod_Cache.get("antibadwords_rule_id", None)

                if antibadwords_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        await rule.edit(enabled=True)

                        antibadwords_enabled = True

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"),
                guild_id=ctx.guild.id,
                antilink_enabled=antilink_enabled,
                antispam_enabled=True,
                antibadwords_enabled=antibadwords_enabled,
            )

            await waiting_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.AUTOMOD} AutoMod has been enabled", color=0x2b2d31).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @automod_command.command(
        name="disable", help="Disable AutoMod system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def automod_command_disable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if not (
                Automod_Cache.get("antilink_enabled", False)
                and Automod_Cache.get("antispam_enabled", False)
                and Automod_Cache.get("antibadwords_enabled", False)
            ):

                return await self.send_denied_embed(ctx, "AutoMod is already disabled")

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Disengaging AutoMod shields...",
                    color=0x2b2d31
                )
            )

            antilink_enabled = Automod_Cache.get("antilink_enabled", False)

            antibadwords_enabled = Automod_Cache.get("antibadwords_enabled", False)

            try:

                antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                if antilink_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        await rule.edit(enabled=False)

                        antilink_enabled = False

                    except:

                        pass

            except:

                pass

            try:

                antibadwords_rule_id = Automod_Cache.get("antibadwords_rule_id", None)

                if antibadwords_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        await rule.edit(enabled=False)

                        antibadwords_enabled = False

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"),
                guild_id=ctx.guild.id,
                antilink_enabled=antilink_enabled,
                antispam_enabled=False,
                antibadwords_enabled=antibadwords_enabled,
            )

            await waiting_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.AUTOMOD} AutoMod has been disabled", color=0x2b2d31).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @commands.hybrid_group(
        name="antispam",
        help="Enable/Disable AntiSpam system",
        with_app_command=True,
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antispam_command(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="AntiSpam Commands",
                description="These are the AutoMod commands",
                color=0x2b2d31,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"\n\n{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name} - {command.help}"

            embed.set_footer(
                text=f"Toxic (7ox4)",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antispam_command.command(
        name="enable", help="Enable AntiSpam system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antispam_command_enable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if Automod_Cache.get("antispam_enabled", False):

                return await self.send_denied_embed(ctx, "AntiSpam is already enabled")

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Enabling AntiSpam system...",
                    color=0x2b2d31,
                )
            )

            try:

                antispam_rule_id = Automod_Cache.get("antispam_rule_id", None)

                if antispam_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antispam_rule_id))

                        await rule.edit(enabled=True)

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antispam_enabled=True
            )

            await waiting_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.AUTOMOD} AntiSpam has been enabled", color=0x2b2d31).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antispam_command.command(
        name="disable", help="Disable AntiSpam system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antispam_command_disable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if not Automod_Cache.get("antispam_enabled", False):

                return await self.send_denied_embed(ctx, "AntiSpam is already disabled")

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Disabling AntiSpam system...",
                    color=0x2b2d31,
                )
            )

            try:

                antispam_rule_id = Automod_Cache.get("antispam_rule_id", None)

                if antispam_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antispam_rule_id))

                        await rule.edit(enabled=False)

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"),
                guild_id=ctx.guild.id,
                antispam_enabled=False,
            )

            await waiting_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.AUTOMOD} AntiSpam has been disabled", color=0x2b2d31).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antispam_command.command(
        name="settings", help="Edit AntiSpam settings", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antispam_command_settings(self, ctx: commands.Context):

        await self.automod_command_antispam(ctx)

    @commands.hybrid_group(
        name="antilink",
        help="Enable/Disable AntiLink system",
        with_app_command=True,
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antilink_command(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="AntiLink Commands",
                description="These are the AutoMod commands",
                color=0x2b2d31,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"\n\n{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name} - {command.help}"

            embed.set_footer(
                text=f"Toxic (7ox4)",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antilink_command.command(
        name="enable", help="Enable AntiLink system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antilink_command_enable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if Automod_Cache.get("antilink_enabled", False):

                return await self.send_denied_embed(ctx, "AntiLink is already enabled")

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Enabling AntiLink system...",
                    color=0x2b2d31,
                )
            )

            try:

                antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                if antilink_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        await rule.edit(enabled=True)

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antilink_enabled=True
            )

            await waiting_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.AUTOMOD} AntiLink has been enabled", color=0x2b2d31).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antilink_command.command(
        name="disable", help="Disable AntiLink system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antilink_command_disable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if not Automod_Cache.get("antilink_enabled", False):

                return await self.send_denied_embed(ctx, "AntiLink is already disabled")

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Disabling AntiLink system...",
                    color=0x2b2d31,
                )
            )

            try:

                antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                if antilink_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        await rule.edit(enabled=False)

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"),
                guild_id=ctx.guild.id,
                antilink_enabled=False,
            )

            await waiting_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.AUTOMOD} AntiLink has been disabled", color=0x2b2d31).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antilink_command.command(
        name="settings", help="Edit AntiLink settings", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antilink_command_settings(self, ctx: commands.Context):

        await self.automod_command_antilink(ctx)

    @commands.hybrid_group(
        name="antibadwords",
        help="Enable/Disable AntiBadWords system",
        with_app_command=True,
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antibadwords_command(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="AntiBadWords Commands",
                description="These are the AutoMod commands",
                color=0x2b2d31,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"\n\n{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name} - {command.help}"

            embed.set_footer(
                text=f"Toxic (7ox4)",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antibadwords_command.command(
        name="enable", help="Enable AntiBadWords system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antibadwords_command_enable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if Automod_Cache.get("antibadwords_enabled", False):

                await ctx.send(
                    embed=discord.Embed(
                        description="AntiBadWords is already enabled", color=0x2b2d31
                    ),
                    delete_after=20,
                )

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Enabling AntiBadWords system...",
                    color=0x2b2d31,
                )
            )

            try:

                antibadwords_rule_id = Automod_Cache.get("antibadwords_rule_id", None)

                if antibadwords_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        await rule.edit(enabled=True)

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"),
                guild_id=ctx.guild.id,
                antibadwords_enabled=True,
            )

            await waiting_message.edit(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.AUTOMOD} AntiBadWords has been enabled",
                    color=0x2b2d31,
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antibadwords_command.command(
        name="disable", help="Disable AntiBadWords system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antibadwords_command_disable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

            if not Automod_Cache.get("antibadwords_enabled", False):

                await ctx.send(
                    embed=discord.Embed(
                        description="AntiBadWords is already disabled",
                        color=0x2b2d31,
                    ),
                    delete_after=20,
                )

                return

            waiting_message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Disabling AntiBadWords system...",
                    color=0x2b2d31,
                )
            )

            try:

                antibadwords_rule_id = Automod_Cache.get("antibadwords_rule_id", None)

                if antibadwords_rule_id:

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        await rule.edit(enabled=False)

                    except:

                        pass

            except:

                pass

            await storage.automod.update(
                id=Automod_Cache.get("id"),
                guild_id=ctx.guild.id,
                antibadwords_enabled=False,
            )

            await waiting_message.edit(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.AUTOMOD} AntiBadWords has been disabled",
                    color=0x2b2d31,
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antibadwords_command.command(
        name="settings", help="Edit AntiBadWords settings", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antibadwords_command_settings(self, ctx: commands.Context):

        await self.automod_command_antibadwords(ctx)

    @automod_command.command(
        name="antilink", help="Enable/Disable AntiLink system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def automod_command_antilink(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            view_timeout = 60

            cancled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 60

            antilink_regex = r"(?:https?:\/\/)?(?:www\.)?(?:discordapp\.com\/invite|discord\.com\/invite|discord\.me|discord\.gg|[^\s]+\.[^\s]+)(?:\/#)?(?:\/invite)?\/?[a-zA-Z0-9-]*"

            async def get_home_embed():

                await check_antilink()

                Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                embed = discord.Embed(
                    description=f"**AntiLink Settings** {self.bot.emoji.AUTOMOD}\n"
                    f"> **Status:** {self.bot.emoji.ENABLED if Automod_Cache.get('antilink_enabled', False) else self.bot.emoji.DISABLED}\n"
                    f"> **Rule ID:** `{Automod_Cache.get('antilink_rule_id','Not Set')}`\n\n"
                    f"**__Whitelists__**\n",
                    color=0x2b2d31
                )

                antilink_whitelist_roles = json.loads(
                    Automod_Cache.get("antilink_whitelist_roles", "[]")
                )

                embed.description += f"> **Roles:** {', '.join([f'<@&{rule_id}>' for rule_id in antilink_whitelist_roles]) if antilink_whitelist_roles else 'None'}\n"

                antilink_whitelist_channels = Automod_Cache.get("antilink_whitelist_channels", [])

                embed.description += f"> **Channels:** {', '.join([f'<#{channel_id}>' for channel_id in antilink_whitelist_channels]) if antilink_whitelist_channels else 'None'}" 

                embed.set_footer(
                    text=f"Toxic (7ox4)",
                    icon_url=self.bot.user.display_avatar.url,
                )

                return embed

            async def check_antilink():

                try:

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                    if not antilink_rule_id:

                        return

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        await storage.automod.update(
                            id=Automod_Cache.get("id"),
                            guild_id=ctx.guild.id,
                            antilink_enabled=False,
                            antilink_rule_id="",
                        )

                        return

                    if Automod_Cache.get("antilink_enabled", False) != rule.enabled:

                        await storage.automod.update(
                            id=Automod_Cache.get("id"),
                            guild_id=ctx.guild.id,
                            antilink_enabled=rule.enabled,
                        )

                        return

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def get_home_view(disabled=False):

                try:

                    await check_antilink()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    view = discord.ui.View(timeout=60)

                    reset_view_timeout()

                    toggle_button = discord.ui.Button(
                        label=(
                            "Click to Enable"
                            if not Automod_Cache.get("antilink_enabled", False)
                            else "Click to Disable"
                        ),
                        style=(
                            discord.ButtonStyle.gray
                            if not Automod_Cache.get("antilink_enabled", False)
                            else discord.ButtonStyle.gray
                        ),
                        custom_id="toggle_antilink",
                        emoji=(
                            self.bot.emoji.ENABLED
                            if not Automod_Cache.get("antilink_enabled", False)
                            else self.bot.emoji.DISABLED
                        ),
                        row=0,
                    )

                    toggle_button.callback = lambda i: toggle_button_callback(i)

                    if not Automod_Cache.get("antilink_rule_id", False):

                        toggle_button.disabled = True

                    view.add_item(toggle_button)

                    run_setup_button = discord.ui.Button(
                        label=(
                            "Run Setup"
                            if not Automod_Cache.get("antilink_rule_id", None)
                            else "Re-Run Setup"
                        ),
                        style=discord.ButtonStyle.primary,
                        custom_id="run_antilink_setup",
                        row=0,
                        emoji=(
                            self.bot.emoji.SETUP
                            if not Automod_Cache.get("antilink_rule_id", None)
                            else self.bot.emoji.LOADING
                        ),
                    )

                    run_setup_button.callback = lambda i: run_setup_button_callback(i)

                    view.add_item(run_setup_button)

                    antilink_whitelist_roles = Automod_Cache.get("antilink_whitelist_roles", [])

                    whitelist_roles_select = discord.ui.RoleSelect(
                        placeholder="Select Whitelisted Roles",
                        min_values=0,
                        max_values=25,
                        default_values=[
                            ctx.guild.get_role(int(rule_id))
                            for rule_id in antilink_whitelist_roles
                        ],
                        custom_id="whitelist_roles_select",
                        row=1,
                    )

                    whitelist_roles_select.callback = (
                        lambda i: whitelist_roles_select_callback(i)
                    )

                    if not Automod_Cache.get("antilink_enabled", False):

                        whitelist_roles_select.disabled = True

                    view.add_item(whitelist_roles_select)

                    antilink_whitelist_channels = Automod_Cache.get("antilink_whitelist_channels", [])

                    whitelist_channels_select = discord.ui.ChannelSelect(
                        placeholder="Select Whitelisted Channels",
                        channel_types=[discord.ChannelType.text],
                        min_values=0,
                        max_values=25,
                        default_values=[
                            await ctx.guild.fetch_channel(int(channel_id))
                            for channel_id in antilink_whitelist_channels
                        ],
                        custom_id="whitelist_channels_select",
                        row=2,
                    )

                    whitelist_channels_select.callback = (
                        lambda i: whitelist_channels_select_callback(i)
                    )

                    if not Automod_Cache.get("antilink_enabled", False):

                        whitelist_channels_select.disabled = True

                    view.add_item(whitelist_channels_select)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def run_setup_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        await rule.delete()

                        rule = None

                    except:

                        rule = None

                    if not rule:

                        try:

                            whitelist_roles = []

                            for role_id in Automod_Cache.get("antilink_whitelist_roles", []):

                                role = ctx.guild.get_role(int(role_id))

                                if role:

                                    whitelist_roles.append(role)

                            whitelist_channels = []

                            for channel_id in Automod_Cache.get("antilink_whitelist_channels", []):

                                channel = await ctx.guild.fetch_channel(int(channel_id))

                                if channel:

                                    whitelist_channels.append(channel)

                            rule = await ctx.guild.create_automod_rule(
                                name=f"AntiLink by {self.bot.user.display_name}",
                                event_type=discord.AutoModRuleEventType.message_send,
                                enabled=True,
                                trigger=discord.AutoModTrigger(
                                    type=discord.AutoModRuleTriggerType.keyword,
                                    keyword_filter=None,
                                    regex_patterns=[antilink_regex],
                                ),
                                actions=[
                                    discord.AutoModRuleAction(
                                        type=discord.AutoModRuleActionType.block_message,
                                        custom_message="You are not allowed to send any kind of links in this server",
                                    )
                                ],
                                exempt_roles=whitelist_roles,
                                exempt_channels=whitelist_channels,
                                reason=f"Automod AntiLink has been created by {ctx.author.display_name}",
                            )

                            await storage.automod.update(
                                id=Automod_Cache.get("id"),
                                guild_id=ctx.guild.id,
                                antilink_enabled=True,
                                antilink_rule_id=rule.id,
                            )

                        except:

                            logger.error(
                                f"Error in file {__file__}: {traceback.format_exc()}"
                            )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=None
                    )

                    nonlocal cancled

                    cancled = True

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def whitelist_channels_select_callback(
                interaction: discord.Interaction,
            ):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    whitelist_channels_ = [
                        channel for channel in interaction.data["values"]
                    ]

                    anti_link_rule_id = Automod_Cache.get("antilink_rule_id", None)

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(anti_link_rule_id)
                        )

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        return

                    whitelist_channels = []

                    for channel_id in whitelist_channels_:

                        channel = await ctx.guild.fetch_channel(int(channel_id))

                        if channel:

                            whitelist_channels.append(channel)

                    try:

                        await rule.edit(
                            exempt_channels=whitelist_channels,
                            reason=f"Automod AntiLink whitelist channels has been updated by {ctx.author.display_name}",
                        )

                    except:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

                    await storage.automod.update(
                        id=Automod_Cache.get("id"),
                        guild_id=ctx.guild.id,
                        antilink_whitelist_channels=[channel.id for channel in whitelist_channels],
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def whitelist_roles_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    whitelist_roles_ = [role for role in interaction.data["values"]]

                    anti_link_rule_id = Automod_Cache.get("antilink_rule_id", None)

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(anti_link_rule_id)
                        )

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        return

                    whitelist_roles = []

                    for role_id in whitelist_roles_:

                        role = ctx.guild.get_role(int(role_id))

                        if role:

                            whitelist_roles.append(role)

                    try:

                        await rule.edit(
                            exempt_roles=whitelist_roles,
                            reason=f"Automod AntiLink whitelist roles has been updated by {ctx.author.display_name}",
                        )

                    except:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

                    await storage.automod.update(
                        id=Automod_Cache.get("id"),
                        guild_id=ctx.guild.id,
                        antilink_whitelist_roles=[role.id for role in whitelist_roles],
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def toggle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    antilink_rule_id = Automod_Cache.get("antilink_rule_id", None)

                    try:

                        rule = await ctx.guild.fetch_automod_rule(int(antilink_rule_id))

                        # if ryletype is not antilink block custom word

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        await storage.automod.update(
                            id=Automod_Cache.get("id"),
                            guild_id=ctx.guild.id,
                            antilink_enabled=False,
                            antilink_rule_id="",
                        )

                        await interaction.message.edit(
                            embed=await get_home_embed(), view=await get_home_view()
                        )

                        return

                    try:

                        whitelist_roles = []

                        for role_id in Automod_Cache.get("antilink_whitelist_roles", []):

                            role = ctx.guild.get_role(int(role_id))

                            if role:

                                whitelist_roles.append(role)

                        whitelist_channels = []

                        for channel_id in Automod_Cache.get("antilink_whitelist_channels", []):

                            channel = await ctx.guild.fetch_channel(int(channel_id))

                            if channel:

                                whitelist_channels.append(channel)

                        await rule.edit(
                            enabled=not Automod_Cache.get("antilink_enabled", False),
                            reason=f"Automod AntiLink has been {'enabled' if not Automod_Cache.get('antilink_enabled',False) else 'disabled'} by {ctx.author.display_name}",
                        )

                    except:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

                    await storage.automod.update(
                        id=Automod_Cache.get("id"),
                        guild_id=ctx.guild.id,
                        antilink_enabled=not Automod_Cache.get(
                            "antilink_enabled", False
                        ),
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            message = await ctx.send(
                embed=await get_home_embed(), view=await get_home_view()
            )

            while not cancled:

                try:

                    view_timeout -= 1

                    if view_timeout <= 0:

                        await message.edit(
                            embed=await get_home_embed(),
                            view=await get_home_view(disabled=True),
                        )

                        break

                    await asyncio.sleep(1)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @automod_command.command(
        name="antibadwords",
        help="Enable/Disable AntiBadWords system",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def automod_command_antibadwords(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            view_timeout = 60

            cancled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 60

            async def get_home_embed():

                await check_antibadwords()

                Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                embed = discord.Embed(
                    title="AntiBadWords Settings",
                    description="These are the AntiBadWords settings",
                    color=(
                        0x2b2d31
                        if Automod_Cache.get("antibadwords_enabled", False)
                        else 0x2b2d31
                    ),
                )

                embed.add_field(
                    name="Status",
                    value=(
                        self.bot.emoji.ENABLED
                        if Automod_Cache.get("antibadwords_enabled", False)
                        else self.bot.emoji.DISABLED
                    ),
                    inline=True,
                )

                embed.add_field(
                    name="Discord AutoMod Role ID",
                    value=f"`{Automod_Cache.get('antibadwords_rule_id','Not Set')}`",
                    inline=True,
                )

                embed.add_field(
                    name="Bad Words",
                    value=(
                        f"||{', '.join(Automod_Cache.get('antibadwords_words', []))}||"
                        if Automod_Cache.get("antibadwords_words")
                        else "Not Set Yet"
                    ),
                    inline=False,
                )

                antibadwords_whitelist_roles = Automod_Cache.get("antibadwords_whitelist_roles", [])

                embed.add_field(
                    name="Whitelisted Roles",
                    value=(
                        "\n".join(
                            [
                                f"<@&{rule_id}>"
                                for rule_id in antibadwords_whitelist_roles
                            ]
                        )
                        if antibadwords_whitelist_roles
                        else "Not Set Yet"
                    ),
                    inline=True,
                )

                antibadwords_whitelist_channels = Automod_Cache.get("antibadwords_whitelist_channels", [])

                embed.add_field(
                    name="Whitelisted Channels",
                    value=(
                        "\n".join(
                            [
                                f"<#{channel_id}>"
                                for channel_id in antibadwords_whitelist_channels
                            ]
                        )
                        if antibadwords_whitelist_channels
                        else "Not Set Yet"
                    ),
                    inline=True,
                )

                embed.set_footer(
                    text=f"Toxic (7ox4)",
                    icon_url=self.bot.user.display_avatar.url,
                )

                return embed

            async def check_antibadwords():

                try:

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    antibadwords_rule_id = Automod_Cache.get(
                        "antibadwords_rule_id", None
                    )

                    if not antibadwords_rule_id:

                        return

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        await storage.automod.update(
                            id=Automod_Cache.get("id"),
                            guild_id=ctx.guild.id,
                            antibadwords_enabled=False,
                            antibadwords_rule_id="",
                        )

                        return

                    if Automod_Cache.get("antibadwords_enabled", False) != rule.enabled:

                        await storage.automod.update(
                            id=Automod_Cache.get("id"),
                            guild_id=ctx.guild.id,
                            antibadwords_enabled=rule.enabled,
                        )

                        return

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def get_home_view(disabled=False):

                try:

                    await check_antibadwords()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    view = discord.ui.View(timeout=60)

                    reset_view_timeout()

                    toggle_button = discord.ui.Button(
                        label=(
                            "Click to Enable"
                            if not Automod_Cache.get("antibadwords_enabled", False)
                            else "Click to Disable"
                        ),
                        style=(
                            discord.ButtonStyle.gray
                            if not Automod_Cache.get("antibadwords_enabled", False)
                            else discord.ButtonStyle.gray
                        ),
                        custom_id="toggle_antibadwords",
                        emoji=(
                            self.bot.emoji.ENABLED
                            if not Automod_Cache.get("antibadwords_enabled", False)
                            else self.bot.emoji.DISABLED
                        ),
                        row=0,
                    )

                    toggle_button.callback = lambda i: toggle_button_callback(i)

                    if not Automod_Cache.get("antibadwords_rule_id", False):

                        toggle_button.disabled = True

                    view.add_item(toggle_button)

                    run_setup_button = discord.ui.Button(
                        label=(
                            "Run Setup"
                            if not Automod_Cache.get("antibadwords_rule_id", None)
                            else "Re-Run Setup"
                        ),
                        style=discord.ButtonStyle.primary,
                        custom_id="run_antibadwords_setup",
                        row=0,
                        emoji=(
                            self.bot.emoji.SETUP
                            if not Automod_Cache.get("antibadwords_rule_id", None)
                            else self.bot.emoji.LOADING
                        ),
                    )

                    run_setup_button.callback = lambda i: run_setup_button_callback(i)

                    view.add_item(run_setup_button)

                    set_bad_words_button = discord.ui.Button(
                        label="Configure Bad Words",
                        style=discord.ButtonStyle.primary,
                        custom_id="set_bad_words",
                        row=1,
                    )

                    set_bad_words_button.callback = (
                        lambda i: set_bad_words_button_callback(i)
                    )

                    if not Automod_Cache.get("antibadwords_enabled", False):

                        set_bad_words_button.disabled = True

                    view.add_item(set_bad_words_button)

                    antibadwords_whitelist_roles = Automod_Cache.get("antibadwords_whitelist_roles", [])

                    whitelist_roles_select = discord.ui.RoleSelect(
                        placeholder="Select Whitelisted Roles",
                        min_values=0,
                        max_values=25,
                        default_values=[
                            ctx.guild.get_role(int(rule_id))
                            for rule_id in antibadwords_whitelist_roles
                        ],
                        custom_id="whitelist_roles_select",
                        row=2,
                    )

                    whitelist_roles_select.callback = (
                        lambda i: whitelist_roles_select_callback(i)
                    )

                    if not Automod_Cache.get("antibadwords_enabled", False):

                        whitelist_roles_select.disabled = True

                    view.add_item(whitelist_roles_select)

                    antibadwords_whitelist_channels = Automod_Cache.get("antibadwords_whitelist_channels", [])

                    whitelist_channels_select = discord.ui.ChannelSelect(
                        placeholder="Select Whitelisted Channels",
                        channel_types=[discord.ChannelType.text],
                        min_values=0,
                        max_values=25,
                        default_values=[
                            await ctx.guild.fetch_channel(int(channel_id))
                            for channel_id in antibadwords_whitelist_channels
                        ],
                        custom_id="whitelist_channels_select",
                        row=3,
                    )

                    whitelist_channels_select.callback = (
                        lambda i: whitelist_channels_select_callback(i)
                    )

                    if not Automod_Cache.get("antibadwords_enabled", False):

                        whitelist_channels_select.disabled = True

                    view.add_item(whitelist_channels_select)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def set_bad_words_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                    class set_words_modal(
                        discord.ui.Modal, title="Configure Bad Words"
                    ):

                        bad_words_field = discord.ui.TextInput(
                            label="Bad Words",
                            placeholder="Comma separated bad words",
                            default=", ".join(
                                AutomodCache.get("antibadwords_words", [])
                            ),
                            required=False,
                            style=discord.TextStyle.long,
                        )

                        async def on_submit(self, interaction: discord.Interaction):

                            try:

                                await interaction.response.defer()

                                AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                                bad_words = [
                                    word.strip()
                                    for word in self.bad_words_field.value.split(",")
                                ]

                                antibadwords_rule_id = AutomodCache.get(
                                    "antibadwords_rule_id", None
                                )

                                try:

                                    rule = await ctx.guild.fetch_automod_rule(
                                        int(antibadwords_rule_id)
                                    )

                                    if (
                                        rule.trigger.type
                                        != discord.AutoModRuleTriggerType.keyword
                                    ):

                                        rule = None

                                except:

                                    rule = None

                                if not rule:

                                    return

                                try:

                                    await rule.edit(
                                        trigger=discord.AutoModTrigger(
                                            type=discord.AutoModRuleTriggerType.keyword,
                                            keyword_filter=[
                                                f"*{keyword}*" for keyword in bad_words
                                            ],
                                        ),
                                        reason=f"Automod AntiBadWords bad words has been updated by {ctx.author.display_name}",
                                    )

                                except:

                                    pass

                                await storage.automod.update(
                                    id=AutomodCache.get("id"),
                                    guild_id=ctx.guild.id,
                                    antibadwords_words=bad_words,
                                )

                                await interaction.message.edit(
                                    embed=await get_home_embed(),
                                    view=await get_home_view(),
                                )

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__}: {traceback.format_exc()}"
                                )

                    await interaction.response.send_modal(set_words_modal())

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def toggle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    antibadwords_rule_id = Automod_Cache.get(
                        "antibadwords_rule_id", None
                    )

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        await storage.automod.update(
                            id=Automod_Cache.get("id"),
                            guild_id=ctx.guild.id,
                            antibadwords_enabled=False,
                            antibadwords_rule_id="",
                        )

                        await interaction.message.edit(
                            embed=await get_home_embed(), view=await get_home_view()
                        )

                        return

                    try:

                        whitelist_roles = []

                        for role_id in Automod_Cache.get("antibadwords_whitelist_roles", []):

                            role = ctx.guild.get_role(int(role_id))

                            if role:

                                whitelist_roles.append(role)

                        whitelist_channels = []

                        for channel_id in Automod_Cache.get("antibadwords_whitelist_channels", []):

                            channel = await ctx.guild.fetch_channel(int(channel_id))

                            if channel:

                                whitelist_channels.append(channel)

                        await rule.edit(
                            enabled=not Automod_Cache.get(
                                "antibadwords_enabled", False
                            ),
                            reason=f"Automod AntiBadWords has been {'enabled' if not Automod_Cache.get('antibadwords_enabled',False) else 'disabled'} by {ctx.author.display_name}",
                        )

                    except:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

                    await storage.automod.update(
                        id=Automod_Cache.get("id"),
                        guild_id=ctx.guild.id,
                        antibadwords_enabled=not Automod_Cache.get(
                            "antibadwords_enabled", False
                        ),
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def run_setup_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    antibadwords_rule_id = Automod_Cache.get(
                        "antibadwords_rule_id", None
                    )

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        await rule.delete()

                        rule = None

                    except:

                        rule = None

                    if not rule:

                        try:

                            whitelist_roles = []

                            for role_id in Automod_Cache.get("antibadwords_whitelist_roles", []):

                                role = ctx.guild.get_role(int(role_id))

                                if role:

                                    whitelist_roles.append(role)

                            whitelist_channels = []

                            for channel_id in Automod_Cache.get("antibadwords_whitelist_channels", []):

                                channel = await ctx.guild.fetch_channel(int(channel_id))

                                if channel:

                                    whitelist_channels.append(channel)

                            rule = await ctx.guild.create_automod_rule(
                                name=f"AntiBadWords by {self.bot.user.display_name}",
                                event_type=discord.AutoModRuleEventType.message_send,
                                enabled=True,
                                trigger=discord.AutoModTrigger(
                                    type=discord.AutoModRuleTriggerType.keyword,
                                    keyword_filter=[
                                        f"*{keyword}*"
                                        for keyword in Automod_Cache.get("antibadwords_words", [])
                                    ],
                                ),
                                actions=[
                                    discord.AutoModRuleAction(
                                        type=discord.AutoModRuleActionType.block_message,
                                        custom_message="You are not allowed to send any kind of bad words in this server",
                                    ),
                                    discord.AutoModRuleAction(
                                        duration=datetime.timedelta(minutes=1),
                                        type=discord.AutoModRuleActionType.timeout,
                                    ),
                                ],
                                exempt_roles=whitelist_roles,
                                exempt_channels=whitelist_channels,
                                reason=f"Automod AntiBadWords has been created by {ctx.author.display_name}",
                            )

                            await storage.automod.update(
                                id=Automod_Cache.get("id"),
                                guild_id=ctx.guild.id,
                                antibadwords_enabled=True,
                                antibadwords_rule_id=rule.id,
                            )

                        except:

                            logger.error(
                                f"Error in file {__file__}: {traceback.format_exc()}"
                            )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=None
                    )

                    nonlocal cancled

                    cancled = True

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def whitelist_channels_select_callback(
                interaction: discord.Interaction,
            ):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    whitelist_channels_ = [
                        channel for channel in interaction.data["values"]
                    ]

                    antibadwords_rule_id = Automod_Cache.get(
                        "antibadwords_rule_id", None
                    )

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        return

                    whitelist_channels = []

                    for channel_id in whitelist_channels_:

                        channel = await ctx.guild.fetch_channel(int(channel_id))

                        if channel:

                            whitelist_channels.append(channel)

                    try:

                        await rule.edit(
                            exempt_channels=whitelist_channels,
                            reason=f"Automod AntiBadWords whitelist channels has been updated by {ctx.author.display_name}",
                        )

                    except:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

                    await storage.automod.update(
                        id=Automod_Cache.get("id"),
                        guild_id=ctx.guild.id,
                        antibadwords_whitelist_channels=[channel.id for channel in whitelist_channels],
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def whitelist_roles_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    Automod_Cache = cache.automod.get(str(ctx.guild.id), {})

                    whitelist_roles_ = [role for role in interaction.data["values"]]

                    antibadwords_rule_id = Automod_Cache.get(
                        "antibadwords_rule_id", None
                    )

                    try:

                        rule = await ctx.guild.fetch_automod_rule(
                            int(antibadwords_rule_id)
                        )

                        if rule.trigger.type != discord.AutoModRuleTriggerType.keyword:

                            rule = None

                    except:

                        rule = None

                    if not rule:

                        return

                    whitelist_roles = []

                    for role_id in whitelist_roles_:

                        role = ctx.guild.get_role(int(role_id))

                        if role:

                            whitelist_roles.append(role)

                    try:

                        await rule.edit(
                            exempt_roles=whitelist_roles,
                            reason=f"Automod AntiBadWords whitelist roles has been updated by {ctx.author.display_name}",
                        )

                    except:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

                    await storage.automod.update(
                        id=Automod_Cache.get("id"),
                        guild_id=ctx.guild.id,
                        antibadwords_whitelist_roles=[role.id for role in whitelist_roles],
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            message = await ctx.send(
                embed=await get_home_embed(), view=await get_home_view()
            )

            while not cancled:

                try:

                    view_timeout -= 1

                    if view_timeout <= 0:

                        await message.edit(
                            embed=await get_home_embed(),
                            view=await get_home_view(disabled=True),
                        )

                        break

                    await asyncio.sleep(1)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @automod_command.command(
        name="antispam", help="Enable/Disable AntiSpam system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def automod_command_antispam(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not cache.automod.get(str(ctx.guild.id), {}):

                await storage.automod.insert(guild_id=ctx.guild.id)

            view_timeout = 60

            canceled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 60

            async def get_home_embed():

                AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                embed = discord.Embed(
                    title="AntiSpam Settings",
                    description="These are the AntiSpam settings",
                    color=(
                        0x2b2d31
                        if AutomodCache.get("antispam_enabled", False)
                        else 0x2b2d31
                    ),
                )

                # antispam_enabled BOOLEAN DEFAULT FALSE,

                # antispam_whitelist_roles JSON DEFAULT '[]',

                # antispam_whitelist_channels JSON DEFAULT '[]',

                # antispam_max_messages INT DEFAULT 5,

                # antispam_max_interval INT DEFAULT 30,

                # antispam_max_mentions INT DEFAULT 5,

                # antispam_max_emojis INT DEFAULT 10,

                # antispam_max_caps INT DEFAULT 50,

                # antispam_punishment TEXT DEFAULT 'mute',

                # antispam_punishment_duration INT DEFAULT 10,

                embed.add_field(
                    name="Status",
                    value=(
                        self.bot.emoji.ENABLED
                        if AutomodCache.get("antispam_enabled", False)
                        else self.bot.emoji.DISABLED
                    ),
                    inline=True,
                )

                embed.add_field(name="", value="", inline=False)

                embed.add_field(
                    name="Anti-Spam Trigger",
                    value=f"More then `{AutomodCache.get('antispam_max_messages',5)}` messages in `{AutomodCache.get('antispam_max_interval',30)}` seconds",
                    inline=True,
                )

                embed.add_field(
                    name="Anti-Mention-Spam Trigger",
                    value=f"More then `{AutomodCache.get('antispam_max_mentions',5)}` mentions in a message",
                    inline=True,
                )

                embed.add_field(name="", value="", inline=False)

                embed.add_field(
                    name="Anti-Emoji-Spam Trigger",
                    value=f"More then `{AutomodCache.get('antispam_max_emojis',10)}` emojis in a message",
                    inline=True,
                )

                embed.add_field(
                    name="Anti-Caps-Spam Trigger",
                    value=f"More then `{AutomodCache.get('antispam_max_caps',50)}%` of caps in a message",
                    inline=True,
                )

                embed.add_field(name="", value="", inline=False)

                embed.add_field(
                    name="Punishment",
                    value=f"{AutomodCache.get('antispam_punishment','mute')} for `{AutomodCache.get('antispam_punishment_duration',10)}` minutes",
                    inline=True,
                )

                embed.add_field(name="", value="", inline=False)

                embed.add_field(
                    name=f"Whitelisted Roles",
                    value=(
                        "\n".join(
                            [
                                f"<@&{role_id}>"
                                for role_id in AutomodCache.get("antispam_whitelist_roles", [])
                            ]
                        )
                        if AutomodCache.get("antispam_whitelist_roles")
                        else "Not Set Yet"
                    ),
                    inline=True,
                )

                embed.add_field(
                    name=f"Whitelisted Channels",
                    value=(
                        "\n".join(
                            [
                                f"<#{channel_id}>"
                                for channel_id in AutomodCache.get("antispam_whitelist_channels", [])
                            ]
                        )
                        if AutomodCache.get("antispam_whitelist_channels")
                        else "Not Set Yet"
                    ),
                    inline=True,
                )

                embed.set_footer(
                    text=f"Toxic (7ox4)",
                    icon_url=self.bot.user.display_avatar.url,
                )

                return embed

            async def get_home_view(disabled=False):

                try:

                    AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                    view = discord.ui.View(timeout=60)

                    reset_view_timeout()

                    toggle_button = discord.ui.Button(
                        label=(
                            "Click to Enable"
                            if not AutomodCache.get("antispam_enabled", False)
                            else "Click to Disable"
                        ),
                        style=(
                            discord.ButtonStyle.gray
                            if not AutomodCache.get("antispam_enabled", False)
                            else discord.ButtonStyle.gray
                        ),
                        custom_id="toggle_antispam",
                        emoji=(
                            self.bot.emoji.ENABLED
                            if not AutomodCache.get("antispam_enabled", False)
                            else self.bot.emoji.DISABLED
                        ),
                        row=0,
                    )

                    toggle_button.callback = lambda i: toggle_button_callback(i)

                    view.add_item(toggle_button)

                    reset_button = discord.ui.Button(
                        label="Reset",
                        emoji=self.bot.emoji.RESET,
                        style=discord.ButtonStyle.red,
                        custom_id="reset_antispam",
                        row=0,
                    )

                    reset_button.callback = lambda i: reset_button_callback(i)

                    if not AutomodCache.get("antispam_enabled", False):

                        reset_button.disabled = True

                    view.add_item(reset_button)

                    whitelist_roles_select = discord.ui.RoleSelect(
                        placeholder="Select Whitelisted Roles",
                        min_values=0,
                        max_values=25,
                        default_values=[
                            ctx.guild.get_role(int(role_id))
                            for role_id in AutomodCache.get("antispam_whitelist_roles", [])
                        ],
                        custom_id="whitelist_roles_select",
                        row=1,
                    )

                    whitelist_roles_select.callback = (
                        lambda i: whitelist_roles_select_callback(i)
                    )

                    if not AutomodCache.get("antispam_enabled", False):

                        whitelist_roles_select.disabled = True

                    view.add_item(whitelist_roles_select)

                    whitelist_channels_select = discord.ui.ChannelSelect(
                        placeholder="Select Whitelisted Channels",
                        channel_types=[discord.ChannelType.text],
                        min_values=0,
                        max_values=25,
                        default_values=[
                            await ctx.guild.fetch_channel(int(channel_id))
                            for channel_id in AutomodCache.get("antispam_whitelist_channels", [])
                        ],
                        custom_id="whitelist_channels_select",
                        row=2,
                    )

                    whitelist_channels_select.callback = (
                        lambda i: whitelist_channels_select_callback(i)
                    )

                    if not AutomodCache.get("antispam_enabled", False):

                        whitelist_channels_select.disabled = True

                    view.add_item(whitelist_channels_select)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def toggle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                    await storage.automod.update(
                        id=AutomodCache.get("id"),
                        guild_id=ctx.guild.id,
                        antispam_enabled=not AutomodCache.get(
                            "antispam_enabled", False
                        ),
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def reset_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                    await storage.automod.update(
                        id=AutomodCache.get("id"),
                        guild_id=ctx.guild.id,
                        antispam_enabled=False,
                        antispam_whitelist_roles="[]",
                        antispam_whitelist_channels="[]",
                        antispam_max_messages=5,
                        antispam_max_interval=30,
                        antispam_max_mentions=5,
                        antispam_max_emojis=10,
                        antispam_max_caps=50,
                        antispam_punishment="mute",
                        antispam_punishment_duration=10,
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def whitelist_roles_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                    whitelist_roles = [role for role in interaction.data["values"]]

                    await storage.automod.update(
                        id=AutomodCache.get("id"),
                        guild_id=ctx.guild.id,
                        antispam_whitelist_roles=whitelist_roles,
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def whitelist_channels_select_callback(
                interaction: discord.Interaction,
            ):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=20,
                        )

                    await interaction.response.defer()

                    AutomodCache = cache.automod.get(str(ctx.guild.id), {})

                    whitelist_channels = [
                        channel for channel in interaction.data["values"]
                    ]

                    await storage.automod.update(
                        id=AutomodCache.get("id"),
                        guild_id=ctx.guild.id,
                        antispam_whitelist_channels=whitelist_channels,
                    )

                    await interaction.message.edit(
                        embed=await get_home_embed(), view=await get_home_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            message = await ctx.send(
                embed=await get_home_embed(), view=await get_home_view()
            )

            while not canceled:

                try:

                    view_timeout -= 1

                    if view_timeout <= 0:

                        await message.edit(
                            embed=await get_home_embed(),
                            view=await get_home_view(disabled=True),
                        )

                        break

                    await asyncio.sleep(1)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @automod_command.command(name="punishment", help="Set the automod punishment")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def automod_punishment(self, ctx, punishment: str):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        punishments = ["warn", "mute", "kick", "ban"]
        if punishment.lower() not in punishments:
            return await self.send_denied_embed(ctx, f"Invalid punishment. Choose from: {', '.join(punishments)}")
        
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antispam_punishment=punishment.lower())
        await self.send_success_embed(ctx, f"Automod punishment set to `{punishment}`")

    @automod_command.group(name="automute", help="Manage automute settings", invoke_without_command=True)
    async def automod_automute(self, ctx):
        await ctx.send_help(ctx.command)

    @automod_automute.command(name="set", help="Set automute threshold and duration")
    async def automod_automute_set(self, ctx, threshold: int, duration: int):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, automute_threshold=threshold, automute_duration=duration)
        await self.send_success_embed(ctx, f"Automute set to `{threshold}` violations with `{duration}`s duration")

    @automod_automute.command(name="disable", help="Disable automute")
    async def automod_automute_disable(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, automute_threshold=0)
        await self.send_success_embed(ctx, "Automute disabled")

    @automod_command.command(name="reset", help="Reset all automod settings")
    async def automod_reset(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        await storage.automod.delete(id=Automod_Cache.get("id"))
        await storage.automod.insert(guild_id=ctx.guild.id)
        await self.send_success_embed(ctx, "Automod settings have been reset")

    @automod_command.group(name="heat", help="Manage heat (rate limit) settings", invoke_without_command=True)
    async def automod_heat(self, ctx):
        await ctx.send_help(ctx.command)

    @automod_heat.command(name="set", help="Set heat max messages and interval")
    async def automod_heat_set(self, ctx, messages: int, interval: int):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, heat_max_messages=messages, heat_interval=interval)
        await self.send_success_embed(ctx, f"Heat set to `{messages}` messages per `{interval}`s")

    @automod_command.group(name="ignore", help="Manage automod whitelists", invoke_without_command=True)
    async def automod_ignore(self, ctx):
        await ctx.send_help(ctx.command)

    @automod_ignore.command(name="user", help="Ignore a user from automod")
    async def automod_ignore_user(self, ctx, user: discord.Member):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        ignored = json.loads(Automod_Cache.get("ignored_users", "[]"))
        if user.id not in ignored:
            ignored.append(user.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, ignored_users=json.dumps(ignored))
        await self.send_success_embed(ctx, f"Ignoring {user.mention} from automod")

    @automod_ignore.command(name="role", help="Ignore a role from automod")
    async def automod_ignore_role(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        ignored = json.loads(Automod_Cache.get("ignored_roles", "[]"))
        if role.id not in ignored:
            ignored.append(role.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, ignored_roles=json.dumps(ignored))
        await self.send_success_embed(ctx, f"Ignoring {role.mention} from automod")

    @automod_ignore.command(name="channel", help="Ignore a channel from automod")
    async def automod_ignore_channel(self, ctx, channel: discord.TextChannel):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        ignored = json.loads(Automod_Cache.get("ignored_channels", "[]"))
        if channel.id not in ignored:
            ignored.append(channel.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, ignored_channels=json.dumps(ignored))
        await self.send_success_embed(ctx, f"Ignoring {channel.mention} from automod")

    @automod_command.group(name="unignore", help="Remove whitelists", invoke_without_command=True)
    async def automod_unignore(self, ctx):
        await ctx.send_help(ctx.command)

    @automod_unignore.command(name="user")
    async def automod_unignore_user(self, ctx, user: discord.Member):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        ignored = json.loads(Automod_Cache.get("ignored_users", "[]"))
        if user.id in ignored:
            ignored.remove(user.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, ignored_users=json.dumps(ignored))
        await self.send_success_embed(ctx, f"No longer ignoring {user.mention}")

    @automod_command.command(name="logging", help="Set automod logging channel")
    async def automod_logging(self, ctx, channel: discord.TextChannel):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, log_channel_id=channel.id)
        await self.send_success_embed(ctx, f"Automod logging set to {channel.mention}")

    @automod_command.command(name="config", help="Show automod configuration")
    async def automod_config(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        embed = discord.Embed(title="Automod Config", color=0x2b2d31)
        embed.add_field(name="Punishment", value=Automod_Cache.get("antispam_punishment", "warn"))
        embed.add_field(name="Logging", value=f"<#{Automod_Cache.get('log_channel_id')}>" if Automod_Cache.get('log_channel_id') else "Not Set")
        # Add more fields...
        await ctx.send(embed=embed)

    @commands.group(name="blword", help="Blacklisted words management", invoke_without_command=True)
    async def blword_group(self, ctx):
        await ctx.send_help(ctx.command)

    @blword_group.command(name="add", help="Add a word to blacklist")
    async def blword_add(self, ctx, *, word: str):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        words = json.loads(Automod_Cache.get("antibadwords_words", "[]"))
        if word.lower() not in words:
            words.append(word.lower())
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antibadwords_words=json.dumps(words))
        await self.send_success_embed(ctx, f"Added `{word}` to blacklist")

    @blword_group.command(name="remove", help="Remove a word from blacklist")
    async def blword_remove(self, ctx, *, word: str):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        words = json.loads(Automod_Cache.get("antibadwords_words", "[]"))
        if word.lower() in words:
            words.remove(word.lower())
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antibadwords_words=json.dumps(words))
        await self.send_success_embed(ctx, f"Removed `{word}` from blacklist")

    @blword_group.group(name="wlrole", help="Whitelisted roles for word blacklist", invoke_without_command=True)
    async def blword_wlrole(self, ctx):
        await ctx.send_help(ctx.command)

    @blword_wlrole.command(name="add")
    async def blword_wlrole_add(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        roles = json.loads(Automod_Cache.get("antibadwords_whitelist_roles", "[]"))
        if role.id not in roles:
            roles.append(role.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antibadwords_whitelist_roles=json.dumps(roles))
        await self.send_success_embed(ctx, f"Whitelisted role {role.mention} for blword")

    @blword_wlrole.command(name="remove")
    async def blword_wlrole_remove(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        roles = json.loads(Automod_Cache.get("antibadwords_whitelist_roles", "[]"))
        if role.id in roles:
            roles.remove(role.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antibadwords_whitelist_roles=json.dumps(roles))
        await self.send_success_embed(ctx, f"Removed {role.mention} from blword whitelist")

    @blword_group.group(name="wlchannel", help="Whitelisted channels for word blacklist", invoke_without_command=True)
    async def blword_wlchannel(self, ctx):
        await ctx.send_help(ctx.command)

    @blword_wlchannel.command(name="add")
    async def blword_wlchannel_add(self, ctx, channel: discord.TextChannel):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        channels = json.loads(Automod_Cache.get("antibadwords_whitelist_channels", "[]"))
        if channel.id not in channels:
            channels.append(channel.id)
            await storage.automod.update(id=Automod_Cache.get("id"), guild_id=ctx.guild.id, antibadwords_whitelist_channels=json.dumps(channels))
        await self.send_success_embed(ctx, f"Whitelisted channel {channel.mention} for blword")

    @blword_group.group(name="punish", help="Set punishment for word blacklist", invoke_without_command=True)
    async def blword_punish(self, ctx):
        await ctx.send_help(ctx.command)

    @blword_punish.command(name="mute")
    async def blword_punish_mute(self, ctx):
        # For simplicity, we'll use a shared punishment or add a new field if needed.
        # Let's assume blword uses the main automod punishment for now or we could add 'antibadwords_punishment'.
        await self.automod_punishment(ctx, "mute")

    @blword_punish.command(name="kick")
    async def blword_punish_kick(self, ctx):
        await self.automod_punishment(ctx, "kick")

    @blword_punish.command(name="ban")
    async def blword_punish_ban(self, ctx):
        await self.automod_punishment(ctx, "ban")


    @automod_command.command(name="wizard", help="Interactive automod setup")
    async def automod_wizard(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Automod_Cache = cache.automod.get(str(ctx.guild.id), {})
        embed = discord.Embed(title="Automod Wizard", description="Interactive setup is being initialized...", color=0x2b2d31)
        await ctx.send(embed=embed)

    @automod_command.command(name="manage", help="Manage automod settings (Alias for config)")
    async def automod_manage(self, ctx):
        await self.automod_config(ctx)

async def setup(bot):
    await bot.add_cog(Automod(bot))
