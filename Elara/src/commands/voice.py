from __future__ import annotations
import discord


from discord.ext import commands


import psutil


import asyncio


import io


import platform


import datetime


import time


import Elara.src.checks.checks as checks


from Elara.memory.cache import cache


import traceback, sys


import re


import storage.afk


import storage.guilds


import storage.shop


import storage.users


from Elara.console.logging import logger


from Elara.style import color


from Elara.workflows import ui


from Elara.utils import pings


from Elara.config.config import BotConfigClass


BotConfig = BotConfigClass()


import storage


from Elara.workflows.afk_delay import afk_delay


from Elara.engine.Bot import AutoShardedBot


class Voice(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Voice"

            category = "Extra"

            description = "Voice related commands"

            hidden = False

            emoji = self.bot.emoji.MICROPHONE

        self.cog_info = cog_info

    async def send_denied_embed(self, ctx: commands.Context, message: str, delete_after: int = 10):
        embed = discord.Embed(
            description=f"{self.bot.emoji.ERROR} {message}",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        return await ctx.send(embed=embed, delete_after=delete_after)

    async def send_success_embed(self, ctx: commands.Context, message: str, delete_after: int = None):
        embed = discord.Embed(
            description=f"{self.bot.emoji.SUCCESS} {message}",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        return await ctx.send(embed=embed, delete_after=delete_after)

    @commands.command(name="vcmute", help="Mute a user in a voice channel", aliases=["vcm"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcmute(self, ctx: commands.Context, member: discord.Member):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "mute_members"):

                return

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            if member.voice.mute:

                return await self.send_denied_embed(ctx, f"{member.mention} is already muted")

            try:

                await member.edit(mute=True)

                await self.send_success_embed(ctx, f"{member.mention} has been muted")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="vcunmute", help="Unmute a user in a voice channel", aliases=["vcu"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcunmute(self, ctx: commands.Context, member: discord.Member):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "mute_members"):

                return

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            if not member.voice.mute:

                return await self.send_denied_embed(ctx, f"{member.mention} is not muted")

            try:

                await member.edit(mute=False)

                await self.send_success_embed(ctx, f"{member.mention} has been unmuted")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="vcdeafen", help="Deafen a user in a voice channel", aliases=["vcd"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdeafen(self, ctx: commands.Context, member: discord.Member):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "deafen_members"):

                return

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            if member.voice.deaf:

                return await self.send_denied_embed(ctx, f"{member.mention} is already deafened")

            try:

                await member.edit(deafen=True)

                await self.send_success_embed(ctx, f"{member.mention} has been deafened")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="vcundeafen", help="Undeafen a user in a voice channel", aliases=["vcud"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcundeafen(self, ctx: commands.Context, member: discord.Member):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "deafen_members"):

                return

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            if not member.voice.deaf:

                return await self.send_denied_embed(ctx, f"{member.mention} is not deafened")

            try:

                await member.edit(deafen=False)

                await self.send_success_embed(ctx, f"{member.mention} has been undeafened")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(name="vcmove", help="Move a user to a voice channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcmove(
        self,
        ctx: commands.Context,
        member: discord.Member,
        channel: discord.VoiceChannel,
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "move_members"):

                return

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            try:

                await member.move_to(channel)

                await self.send_success_embed(ctx, f"{member.mention} has been moved to {channel.mention}")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="vcmoveall",
        help="Move all users in a voice channel to another voice channel",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def vcmoveall(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        new_channel: discord.VoiceChannel = None,
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "manage_channels"):

                return

            if not await checks.check_is_moderator_permissions(ctx, "move_members"):

                return

            if not new_channel:

                if not ctx.author.voice:

                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"You are not in a voice channel",
                            color=0x2b2d31,
                        )
                    )

                new_channel = channel

                channel = ctx.author.voice.channel

            if len(channel.members) == 0:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{channel.mention} has no users", color=0x2b2d31
                    )
                )

            try:

                for member in channel.members:

                    try:

                        await member.move_to(new_channel)

                    except Exception as e:

                        pass

                await self.send_success_embed(ctx, f"All users in {channel.mention} have been moved to {new_channel.mention}")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcdisconnect", help="Disconnect a user from a voice channel", aliases=["vckick"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdisconnect(self, ctx: commands.Context, member: discord.Member):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "move_members"):

                return

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            try:

                await member.move_to(None)
                await self.send_success_embed(ctx, f"{member.mention} has been disconnected from voice")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="vcpull", help="Pull a user to your voice channel", aliases=["pull"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcpull(self, ctx: commands.Context, member: discord.Member):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if not ctx.author.voice:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"You are not in a voice channel", color=0x2b2d31
                    )
                )

            if not member.voice:

                return await self.send_denied_embed(ctx, f"{member.mention} is not in a voice channel")

            try:

                await member.move_to(ctx.author.voice.channel)
                embed = discord.Embed(
                    description=f"**Successfully pulled {member.display_name} to your voice channel** {self.bot.emoji.SUCCESS}",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                await ctx.send(embed=embed)

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    # vcmuteall

    # vcunmuteall

    # vcdeafenall

    # vcundeafenall

    @commands.command(name="vcmuteall", help="Mute all users in a voice channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcmuteall(
        self, ctx: commands.Context, channel: discord.VoiceChannel = None
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "mute_members"):

                return

            if not channel:

                if not ctx.author.voice:

                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"You are not in a voice channel",
                            color=0x2b2d31,
                        )
                    )

                channel = ctx.author.voice.channel

            if len(channel.members) == 0:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{channel.mention} has no users", color=0x2b2d31
                    )
                )

            try:

                for member in channel.members:

                    try:

                        await member.edit(mute=True)

                    except Exception as e:

                        pass

                await self.send_success_embed(ctx, f"All users in {channel.mention} have been muted")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcunmuteall",
        help="Unmute all users in a voice channel",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcunmuteall(
        self, ctx: commands.Context, channel: discord.VoiceChannel = None
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "mute_members"):

                return

            if not channel:

                if not ctx.author.voice:

                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"You are not in a voice channel",
                            color=0x2b2d31,
                        )
                    )

                channel = ctx.author.voice.channel

            if len(channel.members) == 0:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{channel.mention} has no users", color=0x2b2d31
                    )
                )

            try:

                for member in channel.members:

                    try:

                        await member.edit(mute=False)

                    except Exception as e:

                        pass

                await self.send_success_embed(ctx, f"All users in {channel.mention} have been unmuted")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcdeafenall",
        help="Deafen all users in a voice channel",
        aliases=["vcdefall"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdeafenall(
        self, ctx: commands.Context, channel: discord.VoiceChannel = None
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "deafen_members"):

                return

            if not channel:

                if not ctx.author.voice:

                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"You are not in a voice channel",
                            color=0x2b2d31,
                        )
                    )

                channel = ctx.author.voice.channel

            if len(channel.members) == 0:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{channel.mention} has no users", color=0x2b2d31
                    )
                )

            try:

                for member in channel.members:

                    try:

                        await member.edit(deafen=True)

                    except Exception as e:

                        pass

                await self.send_success_embed(ctx, f"All users in {channel.mention} have been deafened")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcundeafenall",
        help="Undeafen all users in a voice channel",
        aliases=["vcundefall"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcundeafenall(
        self, ctx: commands.Context, channel: discord.VoiceChannel = None
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "deafen_members"):

                return

            if not channel:

                if not ctx.author.voice:

                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"You are not in a voice channel",
                            color=0x2b2d31,
                        )
                    )

                channel = ctx.author.voice.channel

            if len(channel.members) == 0:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{channel.mention} has no users", color=0x2b2d31
                    )
                )

            try:

                for member in channel.members:

                    try:

                        await member.edit(deafen=False)

                    except Exception as e:

                        pass

                await self.send_success_embed(ctx, f"All users in {channel.mention} have been undeafened")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcdisconnectall",
        help="Disconnect all users in a voice channel",
        aliases=["vckickall"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdisconnectall(
        self, ctx: commands.Context, channel: discord.VoiceChannel = None
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "move_members"):

                return

            if not channel:

                if not ctx.author.voice:

                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"You are not in a voice channel",
                            color=0x2b2d31,
                        )
                    )

                channel = ctx.author.voice.channel

            if len(channel.members) == 0:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{channel.mention} has no users", color=0x2b2d31
                    )
                )

            try:

                for member in channel.members:

                    try:

                        await member.move_to(None)

                    except Exception as e:

                        pass

                await self.send_success_embed(ctx, f"All users in {channel.mention} have been disconnected")

            except Exception as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occured: {e}", color=0x2b2d31
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


    @commands.command(name="vcdrag", help="Drag all users from a voice channel to yours", aliases=["vcpullall"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def vcdrag(self, ctx: commands.Context, channel: discord.VoiceChannel):
        try:
            if not await checks.check_is_moderator_permissions(ctx, "administrator"):
                return

            if not ctx.author.voice:
                return await self.send_denied_embed(ctx, "You must be in a voice channel to drag others to it.")

            target_channel = ctx.author.voice.channel
            if not channel.members:
                return await self.send_denied_embed(ctx, f"{channel.mention} is empty.")

            moved_count = 0
            for member in channel.members:
                try:
                    await member.move_to(target_channel)
                    moved_count += 1
                except:
                    continue

            await self.send_success_embed(ctx, f"Successfully dragged **{moved_count}** members from {channel.mention} to {target_channel.mention}")

        except Exception as e:
            logger.error(f"Error in vcdrag: {e}")
            await self.send_denied_embed(ctx, "An error occurred while dragging members.")

    @commands.group(name="vcrole", help="Manage voice roles", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_roles=True)
    async def vcrole(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @vcrole.command(name="set", help="Set the voice role")
    async def vcrole_set(self, ctx: commands.Context, role: discord.Role):
        cache_data = cache.vcrole.get(str(ctx.guild.id))
        if not cache_data:
            await storage.vcrole.insert(guild_id=ctx.guild.id, role_id=role.id)
        else:
            await storage.vcrole.update(id=cache_data.get("id"), role_id=role.id)
        await self.send_success_embed(ctx, f"Voice role set to {role.mention}")

    @vcrole.command(name="clear", help="Clear the voice role")
    async def vcrole_clear(self, ctx: commands.Context):
        cache_data = cache.vcrole.get(str(ctx.guild.id))
        if cache_data:
            await storage.vcrole.delete(id=cache_data.get("id"))
        await self.send_success_embed(ctx, "Voice role cleared")

    @vcrole.command(name="show", help="Show the current voice role")
    async def vcrole_show(self, ctx: commands.Context):
        cache_data = cache.vcrole.get(str(ctx.guild.id))
        if not cache_data or not cache_data.get("role_id"):
            return await self.send_denied_embed(ctx, "No voice role set")
        role = ctx.guild.get_role(cache_data.get("role_id"))
        await ctx.send(embed=discord.Embed(description=f"Current voice role: {role.mention if role else 'Unknown Role'}", color=0x2b2d31))

    @commands.group(name="voice", help="Manage your voice channel", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    async def voice_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def get_user_vc(self, ctx):
        for cid, data in cache.j2c.items():
            if data.get('owner_id') == ctx.author.id and data.get('guild_id') == ctx.guild.id:
                channel = ctx.guild.get_channel(int(cid))
                if channel: return channel
        return None

    @voice_group.command(name="lock", help="Lock your voice channel")
    async def voice_lock(self, ctx: commands.Context):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await self.send_success_embed(ctx, "Locked your voice channel.")

    @voice_group.command(name="unlock", help="Unlock your voice channel")
    async def voice_unlock(self, ctx: commands.Context):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await self.send_success_embed(ctx, "Unlocked your voice channel.")

    @voice_group.command(name="private", help="Make your voice channel private")
    async def voice_private(self, ctx: commands.Context):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await self.send_success_embed(ctx, "Made your voice channel private.")

    @voice_group.command(name="unprivate", help="Make your voice channel public")
    async def voice_unprivate(self, ctx: commands.Context):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await self.send_success_embed(ctx, "Made your voice channel public.")

    @voice_group.command(name="kick", help="Kick a user from your voice channel")
    async def voice_kick(self, ctx: commands.Context, member: discord.Member):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        if member.voice and member.voice.channel == channel:
            await member.move_to(None)
            await self.send_success_embed(ctx, f"Kicked {member.mention} from your voice channel.")
        else:
            await self.send_denied_embed(ctx, "User is not in your voice channel.")

    @voice_group.command(name="ban", help="Ban a user from your voice channel")
    async def voice_ban(self, ctx: commands.Context, member: discord.Member):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        await channel.set_permissions(member, connect=False, view_channel=False)
        if member.voice and member.voice.channel == channel:
            await member.move_to(None)
        await self.send_success_embed(ctx, f"Banned {member.mention} from your voice channel.")

    @voice_group.command(name="unban", help="Unban a user from your voice channel")
    async def voice_unban(self, ctx: commands.Context, member: discord.Member):
        channel = await self.get_user_vc(ctx)
        if not channel: return await self.send_denied_embed(ctx, "You don't own a voice channel.")
        await channel.set_permissions(member, overwrite=None)
        await self.send_success_embed(ctx, f"Unbanned {member.mention} from your voice channel.")

    @voice_group.command(name="pull", help="Pull a user to your voice channel")
    async def voice_pull(self, ctx: commands.Context, member: discord.Member):
        await ctx.invoke(self.vcpull, member=member)

    @voice_group.command(name="move", help="Move a user to another voice channel")
    async def voice_move(self, ctx: commands.Context, member: discord.Member, channel: discord.VoiceChannel):
        await ctx.invoke(self.vcmove, member=member, channel=channel)

    @voice_group.command(name="moveall", help="Move everyone to another channel")
    async def voice_moveall(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if not ctx.author.voice: return await self.send_denied_embed(ctx, "You are not in a voice channel.")
        await ctx.invoke(self.vcmoveall, channel=ctx.author.voice.channel, new_channel=channel)

async def setup(bot):
    await bot.add_cog(Voice(bot))
