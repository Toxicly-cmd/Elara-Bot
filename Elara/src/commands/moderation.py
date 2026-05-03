from __future__ import annotations
import discord
from discord.ext import commands
import datetime
import re
import Elara.src.checks.checks as checks
from Elara.memory.cache import cache

import storage.guilds
import storage.ignore_data
import storage.media_channels
from Elara.console.logging import logger

from Elara.style import color
from Elara.utils import pings

from Elara.config.config import BotConfigClass
BotConfig = BotConfigClass()

import traceback, sys

import storage
import asyncio
import json


from Elara.engine.Bot import AutoShardedBot

class ConfirmationView(discord.ui.View):
    def __init__(self, author_id, timeout=30):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This confirmation is not for you.", ephemeral=True)
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This confirmation is not for you.", ephemeral=True)
        self.value = False
        self.stop()
        await interaction.response.defer()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Moderation"
            category = "Main"
            description =  "Moderation commands"
            hidden =  False
            emoji =  self.bot.emoji.MODERATION 
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
        name="purge",
        help="Purge messages in a channel",
        invoke_without_command=True,
        aliases=['clear','clean','c'],
        usage="purge <amount:int>, purge user <user:discord.Member> <amount:int>, purge images <amount:int>, purge links <amount:int>, purge bots <amount:int>"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_command(self,ctx:commands.Context,amount:int):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                return await self.send_denied_embed(ctx, "You can only delete 1000 messages at a time")
            try:
                await ctx.channel.purge(limit=amount+1,reason=f"Purged by {ctx.author}")
                await self.send_success_embed(ctx, f"Deleted {amount} messages", delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await self.send_denied_embed(ctx, "An Error occurred while purging messages")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @purge_command.command(
        name="user",
        help="Purge messages of a user in a channel",
        aliases=["purgeuser"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_user_command(self,ctx:commands.Context,user:discord.Member,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                return await self.send_denied_embed(ctx, "You can only delete 1000 messages at a time")
            try:
                def check(message:discord.Message):
                    return message.author.id == user.id
                deleted = await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages of {user.mention}", delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await self.send_denied_embed(ctx, "An Error occurred while purging messages")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @purge_command.command(
        name="images",
        help="Purge messages containing images in a channel",
        aliases=["image"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_images_command(self,ctx:commands.Context,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                return await self.send_denied_embed(ctx, "You can only delete 1000 messages at a time")
            try:
                def check_images(message:discord.Message):
                    return any(attachment.content_type and attachment.content_type.startswith('image/') for attachment in message.attachments)
                def check(message:discord.Message):
                    return check_images(message) or any(embed.type == 'image' for embed in message.embeds)
                deleted = await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages containing images", delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await self.send_denied_embed(ctx, "An Error occurred while purging messages")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @purge_command.command(
        name="links",
        help="Purge messages containing links in a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_links_command(self,ctx:commands.Context,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                return await self.send_denied_embed(ctx, "You can only delete 100 messages at a time")
            try:
                def check_links(text):
                    pattern = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
                    return True if pattern.match(text) else False
                def check(message:discord.Message):
                    return check_links(message.content)
                await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await self.send_success_embed(ctx, f"Deleted {amount} messages containing links", delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await self.send_denied_embed(ctx, "An Error occurred while purging messages")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @purge_command.command(
        name="bots",
        help="Purge messages of a bot in a channel",
        aliases=["bot", "purgebots"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_bots_command(self,ctx:commands.Context,amount:int=30):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                return await self.send_denied_embed(ctx, "You can only delete 1000 messages at a time")
            try:
                def check(message:discord.Message):
                    return message.author.bot
                deleted = await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages of bots", delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await self.send_denied_embed(ctx, "An Error occurred while purging messages")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @purge_command.command(name="all", help="Purge all messages in a channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_all_command(self, ctx, amount: int = 100):
        await self.purge_command(ctx, amount)

    @purge_command.command(name="mentions", help="Purge messages containing mentions")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_mentions_command(self, ctx, amount: int = 100):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        def check(m): return len(m.mentions) > 0 or len(m.role_mentions) > 0 or m.mention_everyone
        deleted = await ctx.channel.purge(limit=amount+1, check=check)
        await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages containing mentions", delete_after=10)

    @purge_command.command(name="emoji", help="Purge messages containing emojis")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_emoji_command(self, ctx, amount: int = 100):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        custom_emoji_re = re.compile(r'<a?:[a-zA-Z0-9_]+:[0-9]+>')
        unicode_emoji_re = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        def check(m): return custom_emoji_re.search(m.content) or unicode_emoji_re.search(m.content)
        deleted = await ctx.channel.purge(limit=amount+1, check=check)
        await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages containing emojis", delete_after=10)

    @purge_command.command(name="reactions", help="Clear reactions from messages")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_reactions_command(self, ctx, amount: int = 100):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        count = 0
        async for message in ctx.channel.history(limit=amount+1):
            if message.reactions:
                await message.clear_reactions()
                count += 1
        await self.send_success_embed(ctx, f"Cleared reactions from {count} messages", delete_after=10)

    @purge_command.command(name="contain", help="Purge messages containing specific text")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_contain_command(self, ctx, text: str, amount: int = 100):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        def check(m): return text.lower() in m.content.lower()
        deleted = await ctx.channel.purge(limit=amount+1, check=check)
        await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages containing `{text}`", delete_after=10)

    @purge_command.command(name="embed", help="Purge messages containing embeds")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_embed_command(self, ctx, amount: int = 100):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        def check(m): return len(m.embeds) > 0
        deleted = await ctx.channel.purge(limit=amount+1, check=check)
        await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages containing embeds", delete_after=10)

    @purge_command.command(name="files", help="Purge messages containing attachments")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def purge_files_command(self, ctx, amount: int = 100):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        def check(m): return len(m.attachments) > 0
        deleted = await ctx.channel.purge(limit=amount+1, check=check)
        await self.send_success_embed(ctx, f"Deleted {len(deleted)-1} messages containing attachments", delete_after=10)

    @commands.hybrid_command(
        name="ban",
        with_app_command=True,
        help="Ban a user from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=30,type=commands.BucketType.user)
    async def ban_command(self,ctx:commands.Context,user:discord.Member,*,reason:str=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'ban_members'):
                return
            if not await checks.check_if_user_can_be_banned_or_kicked(ctx,user):
                return
            
            confirm_embed = discord.Embed(
                description=f"Are you sure you want to ban **{user.name}**? {self.bot.emoji.BAN}\n> **Reason:** `{reason if reason else 'No Reason Provided'}`",
                color=color.yellow
            )
            view = ConfirmationView(ctx.author.id)
            msg = await ctx.send(embed=confirm_embed, view=view)
            
            await view.wait()
            
            if view.value is None:
                return await msg.edit(content="Timed out...", embed=None, view=None)
            if view.value is False:
                return await msg.edit(content="Cancelled.", embed=None, view=None)

            try:
                ban_embed = discord.Embed(
                    description=f"You have been banned from **{ctx.guild.name}** {self.bot.emoji.BAN}\n> **Reason:** `{reason if reason else 'No Reason Provided'}`\n> **Moderator:** {ctx.author.mention}\n> **Time:** <t:{int(datetime.datetime.now().timestamp())}:F>",
                    color=0x2b2d31
                )
                ban_embed.set_footer(text=f"Server ID: {ctx.guild.id}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                await user.send(embed=ban_embed)
            except:
                logger.warning(f"Couldn't send a DM to the user {user.id} in guild {ctx.guild.id} while banning the user")
            pre_reason = reason if reason else 'No Reason Provided'
            reason = f"Banned by {ctx.author} with reason: {reason if reason else 'No Reason Provided'}"
            await user.ban(reason=reason)
            embed = discord.Embed(
                description=f"Successfully banned **{user.name}** {self.bot.emoji.BAN}\n> **Reason:** `{pre_reason}`",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await msg.edit(embed=embed, view=None)
        except Exception as e:
            logger.error(f"Error while banning user {user.id} in guild {ctx.guild.id} with error {e}")
            return await self.send_denied_embed(ctx, "An Error occurred while banning the user")

    @commands.hybrid_command(
        name="kick",
        with_app_command=True,
        help="Kick a user from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=30,type=commands.BucketType.user)
    async def kick_command(self,ctx:commands.Context,user:discord.Member,*,reason:str=None):
        if not await checks.check_is_moderator_permissions(ctx, 'kick_members'):
            return
        if not await checks.check_if_user_can_be_banned_or_kicked(ctx,user):
            return
        try:
            confirm_embed = discord.Embed(
                description=f"Are you sure you want to kick **{user.name}**? {self.bot.emoji.KICK}\n> **Reason:** `{reason if reason else 'No Reason Provided'}`",
                color=color.yellow
            )
            view = ConfirmationView(ctx.author.id)
            msg = await ctx.send(embed=confirm_embed, view=view)
            
            await view.wait()
            
            if view.value is None:
                return await msg.edit(content="Timed out...", embed=None, view=None)
            if view.value is False:
                return await msg.edit(content="Cancelled.", embed=None, view=None)

            try:
                kick_embed = discord.Embed(
                    description=f"You have been kicked from **{ctx.guild.name}** {self.bot.emoji.KICK}\n> **Reason:** `{reason if reason else 'No Reason Provided'}`\n> **Moderator:** {ctx.author.mention}\n> **Time:** <t:{int(datetime.datetime.now().timestamp())}:F>",
                    color=0x2b2d31
                )
                kick_embed.set_footer(text=f"Server ID: {ctx.guild.id}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                await user.send(embed=kick_embed)
            except:
                logger.warning(f"Couldn't send a DM to the user {user.id} in guild {ctx.guild.id} while kicking the user")
            pre_reason = reason if reason else 'No Reason Provided'
            reason = f"Kicked by {ctx.author} with reason: {reason if reason else 'No Reason Provided'}"
            await user.kick(reason=reason)
            embed = discord.Embed(
                description=f"Successfully kicked **{user.name}** {self.bot.emoji.KICK}\n> **Reason:** `{pre_reason}`",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await msg.edit(embed=embed, view=None)
        except Exception as e:
            logger.error(f"Error while kicking user {user.id} in guild {ctx.guild.id} with error {e}")
            return await self.send_denied_embed(ctx, "An Error occurred while kicking the user")
        

    @commands.hybrid_command(
        name="unban",
        with_app_command=True,
        help="Unban a user from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def unban_command(self,ctx:commands.Context,user:discord.User,*,reason:str=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'ban_members'):
                return
            user_to_unban = None
            async for entry in ctx.guild.bans(limit=None):
                if entry.user.id == user.id:
                    user_to_unban = entry.user
                    break
                
            if not user_to_unban:
                return await self.send_denied_embed(ctx, "The user is not banned")
                return
            try:
                await ctx.guild.unban(user,reason=reason if reason else "No Reason Provided")
                return await self.send_success_embed(ctx, f"{user.mention} has been unbanned. Reason: {reason if reason else 'No Reason Provided'}")
                try:
                    unban_embed = discord.Embed(
                        title=f"You have been unbanned from {ctx.guild.name}",
                        description=f"Reason: {reason if reason else 'No Reason Provided'}\n\nBy: {ctx.author.mention}\nTime: <t:{int(datetime.datetime.now().timestamp())}:F>",
                        color=0x2b2d31
                    )
                    unban_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
                    unban_embed.set_footer(text=f"Server ID: {ctx.guild.id}",icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                    await user.send(embed=unban_embed)
                except:
                    logger.warning(f"Couldn't send a DM to the user {user.id} in guild {ctx.guild.id} while unbanning the user")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                return await self.send_denied_embed(ctx, "An Error occurred while unbanning the user")
                return
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.command(
        name="unbanall",
        help="Unban all users from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=60,type=commands.BucketType.guild)
    async def unbanall_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'ban_members'):
                return
            try:
                banned_users = []
                message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Unbanning all users",color=0x2b2d31))
                async for ban in ctx.guild.bans(limit=None):
                    banned_users.append(ban.user)

                for banned_user in banned_users:
                    try:
                        await ctx.guild.unban(banned_user)
                    except:
                        pass
                await message.edit(embed=discord.Embed(description=f"{len(banned_users)} users have been unbanned",color=0x2b2d31),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unbanning all users",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.command(name="softban", help="Ban and immediately unban a user to clear their messages")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def softban_command(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        if not await checks.check_is_moderator_permissions(ctx, 'ban_members'): return
        if not await checks.check_if_user_can_be_banned_or_kicked(ctx, user): return
        await user.ban(reason=f"Softban by {ctx.author}: {reason}", delete_message_days=7)
        await ctx.guild.unban(user, reason=f"Softban completion by {ctx.author}")
        await self.send_success_embed(ctx, f"Softbanned **{user.name}**")

    @commands.command(name="nuke", help="Recreate the current channel to clear all messages")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def nuke_command(self, ctx, channel: discord.TextChannel = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = channel or ctx.channel
        new_channel = await channel.clone(reason=f"Nuked by {ctx.author}")
        await new_channel.edit(position=channel.position)
        await channel.delete(reason=f"Nuked by {ctx.author}")
        await new_channel.send(embed=discord.Embed(description=f"Channel Nuked by {ctx.author.mention} {self.bot.emoji.SUCCESS}", color=0x2b2d31))

    @commands.command(name="clone", help="Clone a channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def clone_command(self, ctx, channel: discord.TextChannel = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = channel or ctx.channel
        await channel.clone(reason=f"Cloned by {ctx.author}")
        await self.send_success_embed(ctx, f"Successfully cloned {channel.mention}")

    @commands.command(name="slowmode", help="Set the slowmode for a channel", aliases=["sm"])
    @checks.ignore_check()
    @checks.blacklist_check()
    async def slowmode_command(self, ctx, seconds: int, channel: discord.TextChannel = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = channel or ctx.channel
        await channel.edit(slowmode_delay=seconds)
        await self.send_success_embed(ctx, f"Set slowmode to {seconds}s in {channel.mention}")

    @commands.command(name="unslowmode", help="Disable slowmode for a channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def unslowmode_command(self, ctx, channel: discord.TextChannel = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = channel or ctx.channel
        await channel.edit(slowmode_delay=0)
        await self.send_success_embed(ctx, f"Disabled slowmode in {channel.mention}")


    @commands.command(name="enlarge", help="Show a larger version of an emoji")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def enlarge_command(self, ctx, emoji: discord.PartialEmoji):
        embed = discord.Embed(title=f"Emoji: {emoji.name}", color=0x2b2d31)
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)

    @commands.command(name="fakeban", help="Fake ban a user", aliases=["fban"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    async def fakeban(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if user.id == self.bot.user.id: return await ctx.send("I can't ban myself")
        embed = discord.Embed(description=f"Successfully banned **{user.name}** {self.bot.emoji.BAN}\n> Reason: `{reason}`", color=0x2b2d31)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="fakekick", help="Fake kick a user", aliases=["fkick"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    async def fakekick(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if user.id == self.bot.user.id: return await ctx.send("I can't kick myself")
        embed = discord.Embed(description=f"Successfully kicked **{user.name}** {self.bot.emoji.KICK}\n> Reason: `{reason}`", color=0x2b2d31)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    
    @commands.command(
        name='snipe',
        help='Snipe the last deleted message in the channel',
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.channel)
    async def snipe_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            snipe_data = cache.snipe_data.get('delete',{}).get(str(ctx.channel.id))
            if not snipe_data:
                return await self.send_denied_embed(ctx, "No message to snipe")
                return
            message_id = snipe_data.get('message_id')
            content = snipe_data.get('before_content')
            author_id = snipe_data.get('author_id')
            created_at = snipe_data.get('created_at').replace(tzinfo=None)
            embed = discord.Embed(
                description=f"**Message Sniped** {self.bot.emoji.MESSAGE}\n"
                f"**Author:** <@{author_id}>\n"
                f"**Deleted:** <t:{int(created_at.timestamp())}:R>\n\n"
                f"**Content:** {content}",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Message ID: {message_id}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @commands.command(
        name='editsnipe',
        help='Snipe the last edited message in the channel',
        aliases=['esnipe','es']
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.channel)
    async def editsnipe_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            snipe_data = cache.snipe_data.get('edit',{}).get(str(ctx.channel.id))
            if not snipe_data:
                return await self.send_denied_embed(ctx, "No message to snipe")
                return
            message_id = snipe_data.get('message_id')
            before_content = snipe_data.get('before_content')
            after_content = snipe_data.get('after_content')
            author_id = snipe_data.get('author_id')
            created_at = snipe_data.get('created_at').replace(tzinfo=None)
            embed = discord.Embed(
                description=f"Edited snipe from <@{author_id}> {self.bot.emoji.EDIT}\n> **Edited:** <t:{int(created_at.timestamp())}:F>\n> **Before:** {before_content}\n> **After:** {after_content}",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Message ID: {message_id}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    
    # want to make a group name ignore with subcommands user, channel and in the user,channel subcommand want to add a subcommand add and remove and list

    @commands.group(
        name="ignore",
        help="Ignore users or channels",
        invoke_without_command=True,
        usage="ignore user <user:discord.Member>, ignore channel <channel:discord.TextChannel>"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            embed = discord.Embed(
                description=f"**Ignore System** {self.bot.emoji.MODERATION}\nConfigure bypass rules to exempt specific users or channels from bot protocols.\n\n**__Commands:__**\n",
                color=0x2b2d31
            )

            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"> `{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}\n"

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_command.group(
        name="user",
        help="Ignore a user",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            embed = discord.Embed(
                description=f"**Ignore User** {self.bot.emoji.MODERATION}\nManage users exempted from bot protocols.\n\n**__Commands:__**\n",
                color=0x2b2d31
            )
            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.parent.name} {ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_user_command.command(
        name="add",
        help="Ignore a user"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_add_command(self,ctx:commands.Context,member:discord.Member):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{}).get(str(member.id)):
                    return await self.send_denied_embed(ctx, f"{member.mention} is already ignored")
                    return
                await storage.ignore_data.insert(guild_id=ctx.guild.id,user_id=member.id)
                return await self.send_success_embed(ctx, f"{member.mention} has been ignored")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while ignoring the member",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @ignore_user_command.command(
        name="remove",
        help="Unignore a user"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_remove_command(self,ctx:commands.Context,member:discord.Member):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if not cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{}).get(str(member.id)):
                    return await self.send_denied_embed(ctx, f"{member.mention} is not ignored")
                    return
                await storage.ignore_data.delete(guild_id=ctx.guild.id,user_id=member.id)
                return await self.send_success_embed(ctx, f"{member.mention} has been unignored")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unignoring the member",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_user_command.command(
        name="list",
        help="List ignored users"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_list_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                ignored_users = cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{})
                
                if not ignored_users:
                    await ctx.send(embed=discord.Embed(description="No users are ignored",color=0x2b2d31),delete_after=10)
                    return
                ignored_users = list(ignored_users.keys())
                # make ignored_users 5 by 5 list
                ignored_users = [ignored_users[i:i + 5] for i in range(0, len(ignored_users), 5)]
                
                current_page_index = 0
                view_timeout = 60
                cancled = False
                def reset_view_timeout():
                    nonlocal view_timeout
                    view_timeout = 60
                
                async def get_embed():
                    nonlocal ignored_users,current_page_index
                    embed = discord.Embed(
                        description=f"**Ignored Users** {self.bot.emoji.MODERATION}\n" + ', '.join([f"<@{user_id}>" for user_id in ignored_users[current_page_index]]),
                        color=0x2b2d31
                    )
                    embed.set_footer(text=f"Toxic (7ox4) • Page {current_page_index+1}/{len(ignored_users)}", icon_url=self.bot.user.display_avatar.url)
                    return embed
                
                async def get_view(disabled=False):
                    nonlocal view_timeout
                    reset_view_timeout()
                    view = discord.ui.View()
                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.PREVIOUS,
                        row=0,
                        disabled=current_page_index <= 0
                    )
                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.danger,
                        emoji=self.bot.emoji.STOP,
                        row=0,
                        disabled=len(ignored_users) == 1
                    )
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.NEXT,
                        row=0,
                        disabled=current_page_index >= len(ignored_users)-1
                    )
                    previous_button.callback = lambda i: previous_button_callback(i)
                    stop_button.callback = lambda i: stop_button_callback(i)
                    next_button.callback = lambda i: next_button_callback(i)
                    view.add_item(previous_button)
                    view.add_item(stop_button)
                    view.add_item(next_button)
                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                
                async def previous_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index -= 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                async def stop_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal cancled
                        cancled = True
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view(disabled=True))
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                async def next_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index += 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                message = await ctx.send(embed=await get_embed(),view=await get_view())

                while not cancled:
                    view_timeout -= 1
                    if view_timeout <= 0:
                        await message.edit(embed=await get_embed(),view=await get_view(disabled=True))
                        break
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while listing ignored users",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_command.group(
        name="channel",
        help="Ignore a channel",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            embed = discord.Embed(
                description=f"**Ignore Channel** {self.bot.emoji.MODERATION}\nManage channels exempted from bot protocols.\n\n**__Commands:__**\n",
                color=0x2b2d31
            )
            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.parent.name} {ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_channel_command.command(
        name="add",
        help="Ignore a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_add_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is already ignored",color=0x2b2d31),delete_after=10)
                    return
                await storage.ignore_data.insert(guild_id=ctx.guild.id,channel_id=channel.id,type='channel')
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been ignored",color=0x2b2d31),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while ignoring the channel",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @ignore_channel_command.command(
        name="remove",
        help="Unignore a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_remove_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if not cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is not ignored",color=0x2b2d31),delete_after=10)
                    return
                await storage.ignore_data.delete(guild_id=ctx.guild.id,channel_id=channel.id)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been unignored",color=0x2b2d31),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unignoring the channel",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_channel_command.command(
        name="list",
        help="List ignored channels"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_list_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                ignored_channels = cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{})
                
                if not ignored_channels:
                    await ctx.send(embed=discord.Embed(description="No channels are ignored",color=0x2b2d31),delete_after=10)
                    return
                ignored_channels = list(ignored_channels.keys())
                # make ignored_channels 5 by 5 list
                ignored_channels = [ignored_channels[i:i + 5] for i in range(0, len(ignored_channels), 5)]
                
                current_page_index = 0
                view_timeout = 60
                cancled = False
                def reset_view_timeout():
                    nonlocal view_timeout
                    view_timeout = 60
                
                async def get_embed():
                    nonlocal ignored_channels,current_page_index
                    embed = discord.Embed(
                        description=f"**Ignored Channels** {self.bot.emoji.MODERATION}\n" + ', '.join([f"<#{channel_id}>" for channel_id in ignored_channels[current_page_index]]),
                        color=0x2b2d31
                    )
                    embed.set_footer(text=f"Toxic (7ox4) • Page {current_page_index+1}/{len(ignored_channels)}", icon_url=self.bot.user.display_avatar.url)
                    return embed
                
                async def get_view(disabled=False):
                    nonlocal view_timeout
                    reset_view_timeout()
                    view = discord.ui.View()
                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.PREVIOUS,
                        row=0,
                        disabled=current_page_index <= 0
                    )
                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.danger,
                        emoji=self.bot.emoji.STOP,
                        row=0,
                        disabled=len(ignored_channels) == 1
                    )
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.NEXT,
                        row=0,
                        disabled=current_page_index >= len(ignored_channels)-1
                    )
                    previous_button.callback = lambda i: previous_button_callback(i)
                    stop_button.callback = lambda i: stop_button_callback(i)
                    next_button.callback = lambda i: next_button_callback(i)
                    view.add_item(previous_button)
                    view.add_item(stop_button)
                    view.add_item(next_button)
                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                
                async def previous_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index -= 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

                async def stop_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal cancled
                        cancled = True
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view(disabled=True))
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                async def next_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index += 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                message = await ctx.send(embed=await get_embed(),view=await get_view())

                while not cancled:
                    view_timeout -= 1
                    if view_timeout <= 0:
                        await message.edit(embed=await get_embed(),view=await get_view(disabled=True))
                        break
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while listing ignored channels",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.hybrid_command(
        name='lock',
        help='Lock a channel',
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def lock_command(self,ctx:commands.Context,channel:discord.abc.GuildChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'):
                return
            if not channel:
                channel = ctx.channel

            # Check bot permissions
            if not ctx.guild.me.guild_permissions.manage_channels or not ctx.guild.me.guild_permissions.manage_roles:
                return await self.send_denied_embed(ctx, "I am missing `Manage Channels` or `Manage Roles` permissions to lock this channel.")

            try:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                elif isinstance(channel, discord.VoiceChannel):
                    await channel.set_permissions(ctx.guild.default_role, connect=False,send_messages=False)
                else:
                    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                await self.send_success_embed(ctx, f"{channel.mention} has been locked")
            except discord.Forbidden:
                await self.send_denied_embed(ctx, "I don't have enough permissions to modify this specific channel's permissions. Please check my role position and channel overrides.")
        except Exception as e:
            logger.error(f"Error in lock command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @commands.hybrid_command(
        name='unlock',
        help='Unlock a channel',
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def unlock_command(self,ctx:commands.Context,channel:discord.abc.GuildChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'):
                return
            if not channel:
                channel = ctx.channel

            # Check bot permissions
            if not ctx.guild.me.guild_permissions.manage_channels or not ctx.guild.me.guild_permissions.manage_roles:
                return await self.send_denied_embed(ctx, "I am missing `Manage Channels` or `Manage Roles` permissions to unlock this channel.")

            try:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                elif isinstance(channel, discord.VoiceChannel):
                    await channel.set_permissions(ctx.guild.default_role, connect=True,send_messages=True)
                else:
                    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                await self.send_success_embed(ctx, f"{channel.mention} has been unlocked")
            except discord.Forbidden:
                await self.send_denied_embed(ctx, "I don't have enough permissions to modify this specific channel's permissions. Please check my role position and channel overrides.")
        except Exception as e:
            logger.error(f"Error in unlock command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)


    running_lockall = {}
    @commands.hybrid_command(
        name="lockall",
        help="Lock all channels in the server",
        aliases=["lockchannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def lockall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_lockall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another lockall command is already running",color=0x2b2d31),delete_after=10)
                return
            async def lock_channel(channel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(ctx.guild.default_role, connect=False,send_messages=False)
                    else:
                        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                except Exception as e:
                    logger.error(f"Error in lockall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Locking all channels",color=0x2b2d31))
            self.running_lockall[ctx.guild.id] = True
            for channel in ctx.guild.text_channels:
                try:
                    await lock_channel(channel)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_lockall:
                del self.running_lockall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description=f"{self.bot.emoji.LOCK} | All channels have been locked",color=0x2b2d31))
        except Exception as e:
            if ctx.guild.id in self.running_lockall:
                del self.running_lockall[ctx.guild.id]
            logger.error(f"Error in lockall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    


    running_unhideall = {}
    @commands.hybrid_command(
        name="unlockall",
        help="Unlock all channels in the server",
        aliases=["unlockchannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def unlockall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_unhideall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another unlockall command is already running",color=0x2b2d31),delete_after=10)
                return
            async def unlock_channel(channel:discord.abc.GuildChannel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(ctx.guild.default_role, connect=True,send_messages=True)
                    else:
                        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                except Exception as e:
                    logger.error(f"Error in unlockall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Unlocking all channels",color=0x2b2d31))
            self.running_unhideall[ctx.guild.id] = True
            for channel in ctx.guild.channels:
                try:
                    await unlock_channel(channel)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been unlocked",color=0x2b2d31))
        except Exception as e:
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            logger.error(f"Error in unlockall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    @commands.hybrid_command(
        name="hide",
        help="Hide a channel",
        aliases=["hidechannel"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def hide(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels'):
                return
            if not channel:
                channel = ctx.channel

            # Check bot permissions
            if not ctx.guild.me.guild_permissions.manage_channels or not ctx.guild.me.guild_permissions.manage_roles:
                return await self.send_denied_embed(ctx, "I am missing `Manage Channels` or `Manage Roles` permissions to hide this channel.")

            try:
                await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been hidden",color=0x2b2d31))
            except discord.Forbidden:
                await self.send_denied_embed(ctx, "I don't have enough permissions to modify this specific channel's permissions. Please check my role position and channel overrides.")
        except Exception as e:
            logger.error(f"Error in hide command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    running_hideall = {}
    @commands.hybrid_command(
        name="hideall",
        help="Hide all channels in the server",
        aliases=["hidechannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()  
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def hideall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_hideall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another hideall command is already running",color=0x2b2d31),delete_after=10)
                return
            async def hide_channel(channel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == False:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == False and channel.permissions_for(ctx.guild.default_role).connect == False:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=False, connect=False)
                    else:
                        if channel.permissions_for(ctx.guild.default_role).view_channel == False:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                except Exception as e:
                    logger.error(f"Error in hideall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Hiding all channels",color=0x2b2d31))
            self.running_hideall[ctx.guild.id] = True
            for channel in ctx.guild.channels:
                try:
                    await hide_channel(channel)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_hideall:
                del self.running_hideall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been hidden",color=0x2b2d31))
        except Exception as e:
            if ctx.guild.id in self.running_hideall:
                del self.running_hideall[ctx.guild.id]
            logger.error(f"Error in hideall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @commands.hybrid_command(
        name="unhide",
        help="Unhide a channel",
        aliases=["unhidechannel"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def unhide(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels'):
                return
            if not channel:
                channel = ctx.channel

            # Check bot permissions
            if not ctx.guild.me.guild_permissions.manage_channels or not ctx.guild.me.guild_permissions.manage_roles:
                return await self.send_denied_embed(ctx, "I am missing `Manage Channels` or `Manage Roles` permissions to unhide this channel.")

            try:
                await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been unhidden",color=0x2b2d31))
            except discord.Forbidden:
                await self.send_denied_embed(ctx, "I don't have enough permissions to modify this specific channel's permissions. Please check my role position and channel overrides.")
        except Exception as e:
            logger.error(f"Error in unhide command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    running_unhideall = {}
    @commands.hybrid_command(
        name="unhideall",
        help="Unhide all channels in the server",
        aliases=["unhidechannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def unhideall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_unhideall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another unhideall command is already running",color=0x2b2d31),delete_after=10)
                return
            async def unhide_channel(channel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == True:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                    elif isinstance(channel, discord.VoiceChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == True and channel.permissions_for(ctx.guild.default_role).connect == True:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=True, connect=True)
                    else:
                        if channel.permissions_for(ctx.guild.default_role).view_channel == True:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                except Exception as e:
                    logger.error(f"Error in unhideall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Unhiding all channels",color=0x2b2d31))
            self.running_unhideall[ctx.guild.id] = True
            for channel in ctx.guild.channels:
                try:
                    await unhide_channel(channel)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been unhidden",color=0x2b2d31))
        except Exception as e:
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            logger.error(f"Error in unhideall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)


    # main primary command will also will be in slash command
    # role is not in the slashcommand fix it
    @commands.hybrid_group(
        name="role",
        help="Manage roles of the users",
        with_app_command=True,
        invoke_without_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=60,type=commands.BucketType.user)
    # role @member @role
    @discord.app_commands.describe(member="The member to assign or remove the role", role="The role to assign or remove")
    async def role_command(self,ctx:commands.Context,member:discord.Member=None,*,role:discord.Role=None):
        try:
            if not member:
                # show all the commands this group has
                embed = discord.Embed(
                    description=(
                        f"Manage member roles with efficiency and precision {self.bot.emoji.ROLE}\n\n"
                        "**__Commands:__**\n"
                    ),
                    color=0x2b2d31
                )
                embed.description += f"> `{self.bot.BotConfig.PREFIX}{ctx.command.name} <member> <role>` : Toggle a role for a member\n"
                if hasattr(ctx.command,'commands'):
                    for command in ctx.command.commands:
                        embed.description += f"> `{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}\n"
                
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                await ctx.send(embed=embed)
            elif not role:
                return await ctx.send(embed=discord.Embed(description=f"Invalid Syntax\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} <member> <role>`",color=0x2b2d31))


            else:
                try:
                    if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'):
                        return
                    if not await checks.check_if_user_can_manage_this_role(ctx,role):
                        return
                    
                    if role in member.roles:
                        await member.remove_roles(role)
                        await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.DELETE} Removed {role.mention} from {member.mention}",color=0x2b2d31))
                    else:
                        await member.add_roles(role)
                        await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.CREATE} Added {role.mention} to {member.mention}",color=0x2b2d31))          
                except Exception as e:
                    logger.error(f"Error in role command: {e}")
                    await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in role command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)


    running_humans_command = {} # running_humans_command[guild_id] = True/False

    # role humans @role
    @role_command.command(
        name="humans",
        help="Manage roles of the humans in the server",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def role_humans_command(self,ctx:commands.Context,role:discord.Role):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'):
                return
            if not await checks.check_if_user_can_manage_this_role(ctx,role):
                return
            
            if self.running_humans_command.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another humans command is already running",color=0x2b2d31),delete_after=10)
                return

            def calculate_role_delay(user_count: int) -> float:
                # Maximum allowed rate per second
                max_rate_per_second = 16.67
                
                # Calculate delay per role change (in seconds)
                delay_per_user = 1 / max_rate_per_second
                
                # Adding a safety buffer
                safe_delay = delay_per_user + 2 # 0.04 seconds is added as a safety buffer
                
                # Calculate total time required for the given number of users
                total_time = user_count * safe_delay
                
                return safe_delay, total_time
            
            # Get all the humans in the server
            humans = [member for member in ctx.guild.members if not member.bot and role not in member.roles]
            total_humans = len(humans)
            delay_per_user, total_time = calculate_role_delay(total_humans)

            # Send a message aproximating the time required to complete the task
            message = await ctx.send(embed=discord.Embed(description=f"Estimated time to complete the task: <t:{int(datetime.datetime.now().timestamp() + datetime.timedelta(seconds=total_time).total_seconds()+20)}:R>",color=0x2b2d31))
            self.running_humans_command[ctx.guild.id] = True

            # Add the role to all the humans
            added_users = 0
            for human in humans:
                try:
                    if role in human.roles:
                        continue
                    await human.add_roles(role)
                    await asyncio.sleep(delay_per_user)
                    added_users += 1
                except Exception as e:
                    pass
            await message.edit(embed=discord.Embed(description=f"Added {role.mention} to {added_users} users",color=0x2b2d31))
        except Exception as e:
            logger.error(f"Error in role humans command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
        self.running_humans_command[ctx.guild.id] = False


    running_bots_command = {} # running_bots_command[guild_id] = True/False

    # role bots @role
    @role_command.command(
        name="bots",
        help="Manage roles of the bots in the server",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def role_bots_command(self,ctx:commands.Context,role:discord.Role):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'):
                return
            if not await checks.check_if_user_can_manage_this_role(ctx,role):
                return
            
            if self.running_bots_command.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another bots command is already running",color=0x2b2d31),delete_after=10)
                return

            def calculate_role_delay(user_count: int) -> float:
                # Maximum allowed rate per second
                max_rate_per_second = 16.67
                
                # Calculate delay per role change (in seconds)
                delay_per_user = 1 / max_rate_per_second
                
                # Adding a safety buffer
                safe_delay = delay_per_user + 2 # 0.04 seconds is added as a safety buffer
                
                # Calculate total time required for the given number of users
                total_time = user_count * safe_delay
                
                return safe_delay, total_time
            
            # Get all the bots in the server
            bots = [member for member in ctx.guild.members if member.bot and role not in member.roles]
            total_bots = len(bots)
            delay_per_user, total_time = calculate_role_delay(total_bots)

            # Send a message aproximating the time required to complete the task
            message = await ctx.send(embed=discord.Embed(description=f"Estimated time to complete the task: <t:{int(datetime.datetime.now().timestamp() + datetime.timedelta(seconds=total_time).total_seconds()+20)}:R>",color=0x2b2d31))

            self.running_bots_command[ctx.guild.id] = True

            # Add the role to all the bots
            added_users = 0
            for bot in bots:
                try:
                    if role in bot.roles:
                        continue
                    await bot.add_roles(role)
                    await asyncio.sleep(delay_per_user)
                    added_users += 1
                except Exception as e:
                    pass
            await message.edit(embed=discord.Embed(description=f"Added {role.mention} to {added_users} bots",color=0x2b2d31))
        except Exception as e:
            logger.error(f"Error in role bots command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
        self.running_bots_command[ctx.guild.id] = False

    @role_command.command(name="create", help="Create a new role")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def role_create_command(self, ctx, *, name: str):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        role = await ctx.guild.create_role(name=name, reason=f"Created by {ctx.author}")
        await self.send_success_embed(ctx, f"Successfully created role {role.mention}")

    @role_command.command(name="delete", help="Delete a role")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def role_delete_command(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        await role.delete(reason=f"Deleted by {ctx.author}")
        await self.send_success_embed(ctx, f"Successfully deleted role **{role.name}**")

    @role_command.command(name="rename", help="Rename a role")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def role_rename_command(self, ctx, role: discord.Role, *, name: str):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        old_name = role.name
        await role.edit(name=name, reason=f"Renamed by {ctx.author}")
        await self.send_success_embed(ctx, f"Renamed role **{old_name}** to **{name}**")

    @role_command.command(name="colour", help="Change the colour of a role", aliases=["color"])
    @checks.ignore_check()
    @checks.blacklist_check()
    async def role_colour_command(self, ctx, role: discord.Role, colour: discord.Colour):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        await role.edit(colour=colour, reason=f"Colour changed by {ctx.author}")
        await self.send_success_embed(ctx, f"Changed colour of {role.mention} to {colour}")

    @role_command.command(name="icon", help="Change the icon of a role")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def role_icon_command(self, ctx, role: discord.Role, url: str = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        if not ctx.guild.premium_tier >= 2:
            return await self.send_denied_embed(ctx, "Server needs to be Boost Level 2 to use role icons")
        
        if url:
            async with self.bot.session.get(url) as resp:
                if resp.status != 200: return await self.send_denied_embed(ctx, "Could not fetch image")
                icon = await resp.read()
        elif ctx.message.attachments:
            icon = await ctx.message.attachments[0].read()
        else:
            return await self.send_denied_embed(ctx, "Please provide a URL or attach an image")

        await role.edit(display_icon=icon, reason=f"Icon changed by {ctx.author}")
        await self.send_success_embed(ctx, f"Changed icon of {role.mention}")

    @role_command.command(name="all", help="Add a role to all members")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    async def role_all(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        members = [m for m in ctx.guild.members if role not in m.roles]
        if not members: return await ctx.send("Everyone already has this role.")
        await ctx.send(f"Adding {role.mention} to {len(members)} members...")
        count = 0
        for m in members:
            try: await m.add_roles(role); count += 1; await asyncio.sleep(1.5)
            except: pass
        await ctx.send(f"Finished! Added {role.mention} to {count} members.")

    @role_command.command(name="temp", help="Add a temporary role to a user")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def role_temp(self, ctx, member: discord.Member, role: discord.Role, time: str):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        
        # Simple time parser (e.g. 10m, 1h, 1d)
        seconds = 0
        if time.endswith('m'): seconds = int(time[:-1]) * 60
        elif time.endswith('h'): seconds = int(time[:-1]) * 3600
        elif time.endswith('d'): seconds = int(time[:-1]) * 86400
        else: return await ctx.send("Invalid time format. Use 10m, 1h, 1d.")
        
        await member.add_roles(role, reason=f"Temporary role for {time}")
        await self.send_success_embed(ctx, f"Added {role.mention} to {member.mention} for {time}.")
        
        await asyncio.sleep(seconds)
        if role in member.roles:
            await member.remove_roles(role, reason="Temporary role expired")

    @role_command.command(name="taskcancel", help="Cancel a role task (not implemented)")
    async def role_taskcancel(self, ctx):
        await ctx.send("Task cancellation is not yet implemented.")
    @commands.group(name="rrole", help="Remove roles from members", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    async def rrole_group(self, ctx):
        await ctx.send_help(ctx.command)

    @rrole_group.command(name="all", help="Remove a role from all members")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    async def rrole_all(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        members = [m for m in ctx.guild.members if role in m.roles]
        if not members: return await ctx.send("Nobody has this role.")
        await ctx.send(f"Removing {role.mention} from {len(members)} members...")
        count = 0
        for m in members:
            try: await m.remove_roles(role); count += 1; await asyncio.sleep(1.5)
            except: pass
        await ctx.send(f"Finished! Removed {role.mention} from {count} members.")

    @rrole_group.command(name="humans", help="Remove a role from all human members")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    async def rrole_humans(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        members = [m for m in ctx.guild.members if not m.bot and role in m.roles]
        if not members: return await ctx.send("No humans have this role.")
        await ctx.send(f"Removing {role.mention} from {len(members)} humans...")
        count = 0
        for m in members:
            try: await m.remove_roles(role); count += 1; await asyncio.sleep(1.5)
            except: pass
        await ctx.send(f"Finished! Removed {role.mention} from {count} humans.")

    @rrole_group.command(name="bots", help="Remove a role from all bot members")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    async def rrole_bots(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'): return
        if not await checks.check_if_user_can_manage_this_role(ctx, role): return
        members = [m for m in ctx.guild.members if m.bot and role in m.roles]
        if not members: return await ctx.send("No bots have this role.")
        await ctx.send(f"Removing {role.mention} from {len(members)} bots...")
        count = 0
        for m in members:
            try: await m.remove_roles(role); count += 1; await asyncio.sleep(1.5)
            except: pass
        await ctx.send(f"Finished! Removed {role.mention} from {count} bots.")

    @commands.group(name="channel", help="Manage channels in the server", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    async def channel_group(self, ctx):
        await ctx.send_help(ctx.command)

    @channel_group.command(name="create", help="Create a new channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def channel_create(self, ctx, *, name: str):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = await ctx.guild.create_text_channel(name=name, reason=f"Created by {ctx.author}")
        await self.send_success_embed(ctx, f"Created channel {channel.mention}")

    @channel_group.command(name="transfer", help="Move a channel to another category")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def channel_transfer(self, ctx, category: discord.CategoryChannel, channel: discord.TextChannel = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = channel or ctx.channel
        await channel.edit(category=category, reason=f"Transferred by {ctx.author}")
        await self.send_success_embed(ctx, f"Successfully moved {channel.mention} to **{category.name}**")

    @channel_group.command(name="delete", help="Delete a channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def channel_delete(self, ctx, channel: discord.TextChannel = None):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        channel = channel or ctx.channel
        await channel.delete(reason=f"Deleted by {ctx.author}")
        if channel != ctx.channel:
            await self.send_success_embed(ctx, f"Deleted channel **{channel.name}**")

    @channel_group.command(name="rename", help="Rename a channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def channel_rename(self, ctx, channel: discord.TextChannel, *, name: str):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        old_name = channel.name
        await channel.edit(name=name, reason=f"Renamed by {ctx.author}")
        await self.send_success_embed(ctx, f"Renamed {channel.mention} (was **{old_name}**)")

    @channel_group.command(name="deleteafter", help="Set a channel to be deleted after some time")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def channel_deleteafter(self, ctx, channel: discord.TextChannel, time: str):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'): return
        # Logic to delete after time would ideally be a task, but for now we'll just acknowledge
        # For a production bot, you'd store this in a database and have a background task.
        await ctx.send("Delete after functionality is not yet fully implemented with a persistent task, but I've noted the request.")


    @commands.command(
        name="mute",
        help="Mute a member in the server",
        aliases=["timeout"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5,per=60,type=commands.BucketType.user)
    # mute @member 2h[optional] reason[optional]
    async def mute_command(self,ctx:commands.Context,member:discord.Member,time:str,*,reason:str='No reason provided'):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'moderate_members'):
                return
            
            # check if the bot has the required permissions
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send(embed=discord.Embed(description="I don't have the required permissions to mute members",color=0x2b2d31),delete_after=10)
                return

            if member.guild_permissions.administrator:
                await ctx.send(embed=discord.Embed(description=f"{member.mention} is an administrator",color=0x2b2d31),delete_after=10)
                return
            
            if member == ctx.author:
                await ctx.send(embed=discord.Embed(description=f"Dropping a piano on your head...",color=0x2b2d31),delete_after=10)
                return
            
            if member == ctx.guild.me:
                await ctx.send(embed=discord.Embed(description=f"What have I done to you?",color=0x2b2d31),delete_after=10)
                return
            
            if member.top_role >= ctx.author.top_role:
                await ctx.send(embed=discord.Embed(description=f"You can't mute {member.mention} cause their role is higher than you",color=0x2b2d31),delete_after=10)
                return

            if member.top_role >= ctx.guild.me.top_role:
                await ctx.send(embed=discord.Embed(description=f"I can't mute {member.mention} cause their role is higher than me",color=0x2b2d31),delete_after=10)
                return

            if await checks.check_is_owner_raw(member,ctx.guild):
                await ctx.send(embed=discord.Embed(description=f"You can't mute the owner of the server",color=0x2b2d31),delete_after=10)
                return
            
            if member.is_timed_out():
                await ctx.send(embed=discord.Embed(description=f"{member.mention} is already muted",color=0x2b2d31),delete_after=10)
                return
            
            confirm_embed = discord.Embed(
                description=f"Are you sure you want to mute **{member.name}** for `{time}`?\n> **Reason:** `{reason}`",
                color=color.yellow
            )
            view = ConfirmationView(ctx.author.id)
            msg = await ctx.send(embed=confirm_embed, view=view)
            
            await view.wait()
            
            if view.value is None:
                return await msg.edit(content="Timed out...", embed=None, view=None)
            if view.value is False:
                return await msg.edit(content="Cancelled.", embed=None, view=None)

            # convert time from 1s, 1m, 1h, 1d to seconds
            
            try:
                time_str = time.lower()
                if time_str:
                    time_val = time_str.replace('s','').replace('m','*60').replace('h','*60*60').replace('d','*60*60*24')
                    time_seconds = eval(time_val)
            except Exception as e:
                time_seconds = None
                
            try:
                await member.timeout(datetime.timedelta(seconds=time_seconds),reason=reason)
                await msg.edit(content=None, embed=discord.Embed(description=f"{self.bot.emoji.SUCCESS} {member.mention} has been muted for `{time}`", color=0x2b2d31), view=None)
            except Exception as e:
                logger.error(f"Error in mute command: {e}")
                await msg.edit(content="An error occurred while processing the command.", embed=None, view=None)
        except Exception as e:
            logger.error(f"Error in mute command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @commands.group(
        name="unmute",
        help="Unmute a member in the server",
        invoke_without_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5,per=60,type=commands.BucketType.user)
    # unmute @member reason[optional]
    async def unmute_command(self,ctx:commands.Context,member:discord.Member,*,reason:str='No reason provided'):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'moderate_members'):
                return
            
            # check if the bot has the required permissions
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send(embed=discord.Embed(description="I don't have the required permissions to unmute members",color=0x2b2d31),delete_after=10)
                return

            if member.is_timed_out():
                await member.timeout(None,reason=reason)
                await self.send_success_embed(ctx, f"{member.mention} has been unmuted")
            else:
                await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} {member.mention} is not muted",color=0x2b2d31),delete_after=10)
        except Exception as e:
            logger.error(f"Error in unmute command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @unmute_command.command(
        name="all",
        help="Unmute all members in the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=120,type=commands.BucketType.guild)
    async def unmute_all_command(self,ctx:commands.Context,*,reason:str='No reason provided'):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'moderate_members'):
                return
            
            # check if the bot has the required permissions
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send(embed=discord.Embed(description="I don't have the required permissions to unmute members",color=0x2b2d31),delete_after=10)
                return

            muted_members = [member for member in ctx.guild.members if member.is_timed_out()]
            count = 0
            for member in muted_members:
                try:
                    await member.timeout(None,reason=reason)
                    count += 1
                except Exception as e:
                    pass
            await ctx.send(embed=discord.Embed(description=f"Unmuted {len(count)} members out of {len(muted_members)} muted members",color=0x2b2d31))
        except Exception as e:
            logger.error(f"Error in unmute all command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @commands.hybrid_group(
        name="mediachannel",
        help="Manage media channels in the server",
        invoke_without_command=True,
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            
            embed = discord.Embed(
                description=f"Configure and manage dedicated media channels {self.bot.emoji.CHANNEL}\n\n**__Commands:__**\n",
                color=0x2b2d31
            )
            
            formatted_cmds = []
            if hasattr(ctx.command, "commands"):
                for command in ctx.command.commands:
                    formatted_cmds.append(f"> `{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}")
            
            embed.description += "\n".join(formatted_cmds) if formatted_cmds else "No commands available."
            
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in media channel command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @media_channel_command.command(
        name="add",
        help="Add a media channel",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_add_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                if cache.media_channels.get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is already a media channel",color=0x2b2d31),delete_after=10)
                    return
                
                guilds_subscription = cache.guilds.get(str(ctx.guild.id),{}).get('subscription','free')

                if guilds_subscription == 'free':
                    media_channels_limit = 1
                elif guilds_subscription == 'silver_guild_preminum':
                    media_channels_limit = 3
                elif guilds_subscription == 'golden_guild_premium':
                    media_channels_limit = 5
                elif guilds_subscription == 'diamond_guild_premium':
                    media_channels_limit = 10
                else:
                    media_channels_limit = 1
                
                if len(cache.media_channels.get(str(ctx.guild.id),{})) >= media_channels_limit:
                    await ctx.send(embed=discord.Embed(description=f"Media channels limit reached. You can only have {media_channels_limit} media channels",color=0x2b2d31),delete_after=10)
                    return

                await storage.media_channels.insert(guild_id=ctx.guild.id,channel_id=channel.id)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been added as a media channel",color=0x2b2d31),delete_after=10)
            except Exception as e:
                logger.error(f"Error in media channel add command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel add command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @media_channel_command.command(
        name="remove",
        help="Remove a media channel",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_remove_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                if not cache.media_channels.get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is not a media channel",color=0x2b2d31),delete_after=10)
                    return
                await storage.media_channels.delete(guild_id=ctx.guild.id,channel_id=channel.id)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been removed as a media channel",color=0x2b2d31),delete_after=10)
            except Exception as e:
                logger.error(f"Error in media channel remove command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel remove command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @media_channel_command.command(
        name="list",
        help="List media channels",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_list_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                media_channels = cache.media_channels.get(str(ctx.guild.id),{})
                
                if not media_channels:
                    await ctx.send(embed=discord.Embed(description="No media channels are added",color=0x2b2d31),delete_after=10)
                    return
                embed = discord.Embed(
                    title="Media Channels",
                    color=0x2b2d31
                )
                embed.description = ' | '.join([f"<#{channel_id}>" for channel_id in media_channels.keys()])
                embed.set_footer(text=f"Total media channels: {len(media_channels)}")
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in media channel list command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel list command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @media_channel_command.command(
        name='reset',
        help="Reset all media channels",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=120,type=commands.BucketType.guild)
    async def media_channel_reset_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                await storage.media_channels.delete(guild_id=ctx.guild.id)
                await ctx.send(embed=discord.Embed(description="All media channels have been reset",color=0x2b2d31),delete_after=10)
            except Exception as e:
                logger.error(f"Error in media channel reset command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel reset command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @commands.command(
        name="nickname",
        help="Change the nickname of a member",
        aliases=["nick"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=30,type=commands.BucketType.user)
    async def nickname_command(self,ctx:commands.Context,member:discord.Member,*,nickname:str=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_nicknames'):
                return

            if not await checks.check_if_user_can_manage_this_member(ctx,member):
                return
            print (nickname)
            await member.edit(nick=nickname)
            await self.send_success_embed(ctx, f"{member.mention}'s nickname has been changed to `{nickname}`")
        except Exception as e:
            logger.error(f"Error in nickname command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
        



    @commands.group(name="chat", help="Manage chat/fun command access for users", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    async def chat_group(self, ctx):
        await ctx.send_help(ctx.command)

    @chat_group.command(name="ban", help="Ban a user from using fun/chat commands")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def chat_ban(self, ctx, user: discord.Member):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        if user.id in cache.chat_bans.get(str(ctx.guild.id), []):
            return await ctx.send(f"{user.mention} is already chat banned.")
        
        await storage.chat_bans.insert(guild_id=ctx.guild.id, user_id=user.id)
        await self.send_success_embed(ctx, f"Successfully chat banned {user.mention}")

    @chat_group.command(name="unban", help="Unban a user from using fun/chat commands")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def chat_unban(self, ctx, user: discord.Member):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        if user.id not in cache.chat_bans.get(str(ctx.guild.id), []):
            return await ctx.send(f"{user.mention} is not chat banned.")
        
        await storage.chat_bans.delete(guild_id=ctx.guild.id, user_id=user.id)
        await self.send_success_embed(ctx, f"Successfully chat unbanned {user.mention}")

    @chat_group.command(name="banlist", help="List all chat banned users in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def chat_banlist(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'): return
        banned_ids = cache.chat_bans.get(str(ctx.guild.id), [])
        if not banned_ids:
            return await ctx.send("There are no chat banned users in this server.")
        
        mentions = [f"<@{uid}>" for uid in banned_ids]
        embed = discord.Embed(title="Chat Banned Users", description="\n".join(mentions), color=0x2b2d31)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
