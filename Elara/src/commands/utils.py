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


import storage.users


from Elara.console.logging import logger


from Elara.style import color


from Elara.workflows import ui


from Elara.utils import pings


import requests


from Elara.config.config import BotConfigClass


BotConfig = BotConfigClass()


import storage


from Elara.workflows.afk_delay import afk_delay


from Elara.engine.Bot import AutoShardedBot



class ProfileView(discord.ui.View):
    def __init__(self, bot, author, target_user, member=None):
        super().__init__(timeout=60)
        self.bot = bot
        self.author = author
        self.target_user = target_user
        self.member = member
        self.current_type = "avatar_global"

    async def update_embed(self, interaction):
        embed = discord.Embed(color=self.target_user.color if self.target_user.color.value != 0 else 0x2b2d31)
        url = None
        title_text = ""

        if self.current_type == "avatar_global":
            url = self.target_user.display_avatar.url
            title_text = f"**{self.target_user.display_name}'s Global Avatar**"
        elif self.current_type == "avatar_server":
            if self.member and self.member.guild_avatar:
                url = self.member.guild_avatar.url
                title_text = f"**{self.target_user.display_name}'s Server Avatar**"
            else:
                url = self.target_user.display_avatar.url
                title_text = f"**{self.target_user.display_name}'s Global Avatar** (No Server Avatar)"
        elif self.current_type == "banner_global":
            user = await self.bot.fetch_user(self.target_user.id)
            if user.banner:
                url = user.banner.url
                title_text = f"**{self.target_user.display_name}'s Global Banner**"
            else:
                return await interaction.response.send_message("This user has no global banner.", ephemeral=True)
        elif self.current_type == "banner_server":
            # Discord doesn't have a specific "server banner" for members yet, 
            # usually users mean the global banner or we can show the server's banner
            # but user request said "their server banner" which usually implies member banner.
            # member.banner is the same as user.banner if not set per guild (which isn't a feature yet).
            # So I'll show the server's banner as an alternative or just notify.
            guild = interaction.guild
            if guild.banner:
                url = guild.banner.url
                title_text = f"**{guild.name}'s Server Banner**"
            else:
                return await interaction.response.send_message("This server has no banner.", ephemeral=True)

        embed.description = f"{title_text} {self.bot.emoji.MESSAGE}"
        embed.set_image(url=url)
        embed.set_footer(text=f"Toxic (7ox4) • Requested by @{self.author.name}", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Global AV", style=discord.ButtonStyle.secondary)
    async def global_av(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_type = "avatar_global"
        await self.update_embed(interaction)

    @discord.ui.button(label="Server AV", style=discord.ButtonStyle.secondary)
    async def server_av(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_type = "avatar_server"
        await self.update_embed(interaction)

    @discord.ui.button(label="Global BN", style=discord.ButtonStyle.secondary)
    async def global_bn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_type = "banner_global"
        await self.update_embed(interaction)

    @discord.ui.button(label="Server BN", style=discord.ButtonStyle.secondary)
    async def server_bn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_type = "banner_server"
        await self.update_embed(interaction)
class Utils(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Utils"

            category = "Extra"

            description = "Utility commands"

            hidden = False

            emoji = self.bot.emoji.UTILS

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

    @commands.hybrid_command(
        name="ping", with_app_command=True, help="Get The Bot's Ping"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def ping_command(self, ctx: commands.Context):

        try:

            bot_ping = pings.bot(self.bot)

            cache_response_time = pings.cache()

            database_response_time = await pings.database()

            logger.info(
                f"Bot Ping: {bot_ping}ms, Database Response Time: {database_response_time}ms, Cache Response Time: {cache_response_time}ms"
            )

            embed = discord.Embed(
                description=f"**{self.bot.user.display_name} Latency** {self.bot.emoji.LATENCY}\n"
                f"> **Bot:** `{bot_ping}ms`\n"
                f"> **Storage:** `{database_response_time}ms`\n"
                f"> **Cache:** `{cache_response_time}ms`",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Fetching The Ping")

    @commands.hybrid_command(
        name="invite", with_app_command=True, help="Invite The Bot To Your Server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def invite_command(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                description=(
                    f"Expand your server with professional security {self.bot.emoji.INVITE}\n\n"
                    "**__Details:__**\n"
                    "> Click the button below to add me.\n"
                    "> Ensure you have `Manage Server` permissions."
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            view.add_item(
                discord.ui.Button(
                    emoji=self.bot.emoji.INVITE,
                    label="Invite Me",
                    url=self.bot.urls.INVITE,
                )
            )

            # send as ephemeral if its a slash command

            await ctx.send(embed=embed, view=view, mention_author=False)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Sending The Invite Link")

    @commands.hybrid_command(
        name="support", with_app_command=True, help="Join The Support Server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def support_command(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                description=(
                    f"Join our official support community for updates and assistance {self.bot.emoji.SUPPORT}\n\n"
                    "**__Community:__**\n"
                    "> Click the button below to join.\n"
                    "> Please follow the server guidelines."
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            view.add_item(
                discord.ui.Button(label="Support", url=self.bot.urls.SUPPORT_SERVER)
            )

            # send as ephemeral if its a slash command

            await ctx.send(embed=embed, view=view, mention_author=False)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Sending The Support Server Link")

    @commands.hybrid_command(
        name="vote", with_app_command=True, help="Vote For The Bot"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def vote_command(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                description=(
                    f"Help us grow by voting for the bot on various platforms {self.bot.emoji.VOTE}\n\n"
                    "**__Action:__**\n"
                    "> Click the button below to vote.\n"
                    "> You can vote once every 12 hours."
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            view.add_item(discord.ui.Button(label="Vote", url=self.bot.urls.VOTE))

            # send as ephemeral if its a slash command

            await ctx.send(embed=embed, view=view, mention_author=False)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Sending The Voting Link")

    @commands.hybrid_command(
        name="stats",
        with_app_command=True,
        help="Get The Bot's Stats",
        aliases=["statistics", "status"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def stats_command(self, ctx: commands.Context):

        # show the cpu uses and memory uses in % also the os and the python version

        try:

            cpu_usage = psutil.cpu_percent()

            memory_usage = psutil.virtual_memory().percent

            os_name = platform.uname().system

            python_version = platform.python_version()

            embed = discord.Embed(color=0x2b2d31, type="rich")

            # embed.set_author(

            #     name=f"{self.bot.user.display_name} Status",

            #     icon_url=self.bot.user.display_avatar.url

            # )

            def format_number(num):

                return num

                # replace it with the below code if you want to format the numbers

                # if num >= 1_000_000_000:

                #     return f"{num / 1_000_000_000:.1f}b"

                # elif num >= 1_000_000:

                #     return f"{num / 1_000_000:.1f}m"

                # elif num >= 1_000:

                #     return f"{num / 1_000:.1f}k"

                # else:

                #     return str(num)

            embed.description = (
                f"**{self.bot.user.display_name} Statistics** {self.bot.emoji.BOT}\n"
                f"> `Users` : **{format_number(sum([guild.member_count for guild in self.bot.guilds if guild.member_count]))}**\n"
                f"> `Guilds` : **{format_number(len(self.bot.guilds))}**\n"
                f"> `Python` : **{python_version}**\n"
                f"> `Dsc-py` : **{discord.__version__}**\n"
                f"> `BotCpu` : **{cpu_usage}%**\n"
                f"> `BotRam` : **{memory_usage}%**\n"
                f"> `Shards` : **{self.bot.shard_count}**\n"
                f"> `HostOS` : **{os_name}**\n\n"
                f"> [Invite]({self.bot.urls.INVITE}) | [Support]({self.bot.urls.SUPPORT_SERVER}) | [Vote]({self.bot.urls.VOTE})\n"
                f"-# Hosted on shadowhost.fun"
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            invite_me_button = discord.ui.Button(
                label="Invite",
                emoji=self.bot.emoji.INVITE,
                style=discord.ButtonStyle.gray,
                url=self.bot.urls.INVITE,
            )

            support_server_button = discord.ui.Button(
                label="Server",
                emoji=self.bot.emoji.SUPPORT,
                style=discord.ButtonStyle.gray,
                url=self.bot.urls.SUPPORT_SERVER,
            )

            view.add_item(support_server_button)

            view.add_item(invite_me_button)

            await ctx.send(embed=embed, view=view)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Fetching The Stats")

    @commands.command(
        name="steal", help="Can Be Used To Steal Emoji/Multiple Emojis From A Server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    async def steal_command(self, ctx: commands.Context, *emojis: discord.PartialEmoji):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "manage_emojis"):
                return await self.send_denied_embed(ctx, "You Need The Manage Emojis Permission To Use This Command")

            if not emojis:

                # check if the command is replied to a message

                replied_message = ctx.message.reference

                if not replied_message:

                    return await ctx.send(
                        embed=discord.Embed(
                            description="Please Provide Some Custom Emojis To Steal or Reply To A Message With Custom Stickers",
                            color=0x2b2d31,
                        ),
                        delete_after=10,
                    )

                reply_message = await ctx.channel.fetch_message(
                    replied_message.message_id
                )

                if not reply_message:

                    return await ctx.send(
                        embed=discord.Embed(
                            description="Please Provide Some Custom Emojis To Steal or Reply To A Message With Custom Stickers",
                            color=0x2b2d31,
                        ),
                        delete_after=10,
                    )

                stickers = reply_message.stickers

                if not stickers:

                    # try to get the emojis from the message

                    raw_emojis = re.findall(r"<a?:\w+:\d+>", reply_message.content)

                    stickers = []

                    for raw_emoji in raw_emojis:

                        try:

                            # also get those emojis which the bot can't see

                            # emoji = self.bot.get_emoji(int(raw_emoji.split(":")[-1].replace(">","")))

                            emoji = await commands.PartialEmojiConverter().convert(
                                ctx, raw_emoji
                            )

                            if emoji:

                                stickers.append(emoji)

                        except Exception as e:

                            logger.error(
                                f"Error in file {__file__}: {traceback.format_exc()}"
                            )

                            logger.warning(
                                f"Failed To Convert Emoji {raw_emoji} Error: {e}"
                            )

                    if not stickers:

                        return await ctx.send(
                            embed=discord.Embed(
                                description="Please Provide Some Custom Emojis To Steal or Reply To A Message With Custom Stickers",
                                color=0x2b2d31,
                            ),
                            delete_after=10,
                        )

                # check if the guild have enough space to add the emojis

                # guild_stickers = await ctx.guild.fetch_stickers()

                # sticket_limit = ctx.guild.sticker_limit

                view_timeout_time = 60

                cancled = False

                added = False

                added_title = None

                async def get_embed():

                    sticker = stickers[current_page_index]

                    embed = discord.Embed(
                        title="Add as Emoji or Sticker" if not added else added_title,
                        color=0x2b2d31,
                    )

                    embed.set_image(url=sticker.url)

                    embed.set_footer(
                        text=f"{current_page_index+1}/{len(stickers)} Stickers",
                        icon_url=ctx.bot.user.display_avatar.url,
                    )

                    return embed

                current_page_index = 0

                async def get_view(disabled=False):

                    view = discord.ui.View(timeout=60)

                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Previous",
                        row=1,
                        disabled=current_page_index <= 0,
                    )

                    previous_button.callback = lambda i: previous_button_callback(i)

                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=1
                    )

                    stop_button.callback = lambda i: stop_button_callback(i)

                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Next",
                        row=1,
                        disabled=current_page_index >= len(stickers) - 1,
                    )

                    next_button.callback = lambda i: next_button_callback(i)

                    add_as_emoji_button = discord.ui.Button(
                        label="Add as Emoji", style=discord.ButtonStyle.gray, row=0
                    )

                    add_as_emoji_button.callback = (
                        lambda i: add_as_emoji_button_callback(i)
                    )

                    add_as_sticker_button = discord.ui.Button(
                        label="Add as Sticker", style=discord.ButtonStyle.gray, row=0
                    )

                    add_as_sticker_button.callback = (
                        lambda i: add_as_sticker_button_callback(i)
                    )

                    if not added:

                        view.add_item(add_as_emoji_button)

                        view.add_item(add_as_sticker_button)

                    if len(stickers) > 1:

                        view.add_item(previous_button)

                        # view.add_item(stop_button)

                        view.add_item(next_button)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                async def previous_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def stop_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                async def next_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def add_as_emoji_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Emoji",
                                color=0x2b2d31,
                            ),
                            view=None,
                        )

                        added_emojis = []

                        failed_emojis = []

                        for sticker in stickers:

                            try:

                                added_emoji = await ctx.guild.create_custom_emoji(
                                    name=sticker.name.strip("_"),
                                    image=await sticker.read(),
                                    reason=f"Emoji Added By {ctx.author.name}",
                                )

                                added_emojis.append(added_emoji)

                            except Exception as e:

                                failed_emojis.append(sticker)

                                logger.error(
                                    f"Error in file {__file__}: {traceback.format_exc()}"
                                )

                                logger.warning(
                                    f"Falied To Add Emoji {sticker.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Emojis Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                async def add_as_sticker_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Sticker",
                                color=0x2b2d31,
                            ),
                            view=None,
                        )

                        added_stickers = []

                        failed_stickers = []

                        for sticker in stickers:

                            try:

                                image_bytes = await sticker.read()

                                # Creating a discord.File from the bytes

                                image_file = discord.File(
                                    io.BytesIO(image_bytes),
                                    filename=f"{sticker.name}.{'png'}",
                                )

                                added_sticker = await ctx.guild.create_sticker(
                                    name=sticker.name,
                                    emoji="🤖",
                                    description=f"Sticker Added By {ctx.author.name}",
                                    reason=f"Sticker Added By {ctx.author.name}",
                                    file=image_file,
                                )

                                added_stickers.append(added_sticker)

                            except Exception as e:

                                failed_stickers.append(sticker)

                                logger.warning(
                                    f"Falied To Add Sticker {sticker.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Stickers Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                message = await ctx.send(embed=await get_embed(), view=await get_view())

                while not cancled:

                    view_timeout_time -= 1

                    if view_timeout_time <= 0:

                        await message.edit(view=await get_view(True))

                        break

                    await asyncio.sleep(1)

            else:

                for emoji in emojis:

                    if not emoji.is_custom_emoji():

                        return await ctx.send(
                            embed=discord.Embed(
                                description="Please Provide Some Custom Emojis To Steal",
                                color=0x2b2d31,
                            ),
                            delete_after=10,
                        )

                view_timeout_time = 60

                cancled = False

                added = False

                added_title = None

                async def get_embed():

                    emoji = emojis[current_page_index]

                    embed = discord.Embed(
                        title="Add as Emoji or Sticker" if not added else added_title,
                        color=0x2b2d31,
                    )

                    embed.set_image(url=emoji.url)

                    embed.set_footer(
                        text=f"{current_page_index+1}/{len(emojis)} Emojis",
                        icon_url=ctx.bot.user.display_avatar.url,
                    )

                    return embed

                current_page_index = 0

                async def get_view(disabled=False):

                    view = discord.ui.View(timeout=65)

                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Previous",
                        row=1,
                        disabled=current_page_index <= 0,
                    )

                    previous_button.callback = lambda i: previous_button_callback(i)

                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=1
                    )

                    stop_button.callback = lambda i: stop_button_callback(i)

                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Next",
                        row=1,
                        disabled=current_page_index >= len(emojis) - 1,
                    )

                    next_button.callback = lambda i: next_button_callback(i)

                    add_as_emoji_button = discord.ui.Button(
                        label="Add as Emoji", style=discord.ButtonStyle.gray, row=0
                    )

                    add_as_emoji_button.callback = (
                        lambda i: add_as_emoji_button_callback(i)
                    )

                    add_as_sticker_button = discord.ui.Button(
                        label="Add as Sticker", style=discord.ButtonStyle.gray, row=0
                    )

                    add_as_sticker_button.callback = (
                        lambda i: add_as_sticker_button_callback(i)
                    )

                    if not added:

                        view.add_item(add_as_emoji_button)

                        view.add_item(add_as_sticker_button)

                    if len(emojis) > 1:

                        view.add_item(previous_button)

                        # view.add_item(stop_button)

                        view.add_item(next_button)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                async def previous_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def stop_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                async def next_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def add_as_emoji_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Emoji",
                                color=0x2b2d31,
                            ),
                            view=None,
                        )

                        added_emojis = []

                        failed_emojis = []

                        for emoji in emojis:

                            try:

                                added_emoji = await ctx.guild.create_custom_emoji(
                                    name=emoji.name,
                                    image=await emoji.read(),
                                    reason=f"Emoji Added By {ctx.author.name}",
                                )

                                added_emojis.append(added_emoji)

                            except Exception as e:

                                failed_emojis.append(emoji)

                                logger.warning(
                                    f"Falied To Add Emoji {emoji.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Emojis Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                async def add_as_sticker_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Sticker",
                                color=0x2b2d31,
                            ),
                            view=None,
                        )

                        added_stickers = []

                        failed_stickers = []

                        for emoji in emojis:

                            try:

                                image_bytes = await emoji.read()

                                # Creating a discord.File from the bytes

                                image_file = discord.File(
                                    io.BytesIO(image_bytes),
                                    filename=f"{emoji.name}.{'gif' if emoji.animated else 'png'}",
                                )

                                added_sticker = await ctx.guild.create_sticker(
                                    name=emoji.name,
                                    emoji="🤖",
                                    description=f"Sticker Added By {ctx.author.name}",
                                    reason=f"Sticker Added By {ctx.author.name}",
                                    file=image_file,
                                )

                                added_stickers.append(added_sticker)

                            except Exception as e:

                                failed_stickers.append(emoji)

                                logger.warning(
                                    f"Falied To Add Sticker {emoji.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Stickers Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                message = await ctx.send(embed=await get_embed(), view=await get_view())

                while not cancled:

                    view_timeout_time -= 1

                    if view_timeout_time <= 0:

                        await message.edit(view=await get_view(True))

                        break

                    await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="noprefix",
        with_app_command=True,
        help="Enable/Disable The No Prefix Feature",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def noprefix_command(self, ctx: commands.Context):

        try:

            async def get_embed():

                users_cache = cache.users.get(str(ctx.author.id), {})

                embed = discord.Embed(
                    title="No Prefix Feature",
                    color=0x2b2d31 if users_cache.get("no_prefix") else 0x2b2d31,
                )

                embed.description = f"**__Status:__** {self.bot.emoji.ENABLED if users_cache.get('no_prefix') else self.bot.emoji.DISABLED}"

                embed.description += f"\n**__Subscription:__** {self.bot.emoji.ENABLED if users_cache.get('no_prefix_subscription') else self.bot.emoji.DISABLED}"

                if users_cache.get("no_prefix_subscription"):

                    subscription_end = users_cache.get("no_prefix_end")

                    subscription_end_text = (
                        f"<t:{int(subscription_end.timestamp())}:R>"
                        if subscription_end
                        else "`Never`"
                    )

                    embed.description += (
                        f"\n**__Subscription Ends:__** {subscription_end_text}"
                    )

                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                return embed

            timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled=False):

                users_cache = cache.users.get(str(ctx.author.id), {})

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                enable_disable_button = discord.ui.Button(
                    label=(
                        "Click To Enable"
                        if not users_cache.get("no_prefix")
                        else "Click To Disable"
                    ),
                    style=(
                        discord.ButtonStyle.gray
                        if not users_cache.get("no_prefix")
                        else discord.ButtonStyle.gray
                    ),
                    row=0,
                    emoji=(
                        self.bot.emoji.ENABLED
                        if not users_cache.get("no_prefix")
                        else self.bot.emoji.DISABLED
                    ),
                )

                enable_disable_button.callback = (
                    lambda i: enable_disable_button_callback(i)
                )

                enable_disable_subscription_button = discord.ui.Button(
                    label="Subscription Required",
                    style=discord.ButtonStyle.link,
                    url=self.bot.urls.SUPPORT_SERVER,
                    row=0,
                    emoji=self.bot.emoji.SUPPORT,
                )

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    row=0,
                    emoji=self.bot.emoji.CANCLED,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                if users_cache.get("no_prefix_subscription", False):

                    view.add_item(enable_disable_button)

                    view.add_item(cancle_button)

                else:

                    view.add_item(enable_disable_subscription_button)

                    nonlocal cancled

                    cancled = True

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def enable_disable_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer()

                    users_cache = cache.users.get(str(ctx.author.id), {})

                    await storage.users.update(
                        id=users_cache.get("id"),
                        user_id=ctx.author.id,
                        no_prefix=not users_cache.get("no_prefix"),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="afk",
        with_app_command=True,
        help="Set Your AFK Status",
        aliases=["away"],
        usage="<1m/1h/1d> <reason(OPTIONAL)>",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def afk_command(
        self, ctx: commands.Context, time: str = None, *, reason: str = None
    ):

        try:

            if time:

                time = time.lower()

                try:

                    if time.endswith("m"):

                        time = int(time[:-1]) * 60

                    elif time.endswith("h"):

                        time = int(time[:-1]) * 60 * 60

                    elif time.endswith("d"):

                        time = int(time[:-1]) * 60 * 60 * 24

                    elif time.endswith("s"):

                        time = int(time[:-1])

                    else:

                        time = int(time)

                except:

                    reason = f"{time} {reason if reason else ''}"

                    time = None

            else:

                time = None

            if not reason:

                reason = "No Reason Provided"

            # by using re check the reason if it contains any mentions or urls

            if re.search(r"<@!?\d{17,19}>", reason) or re.search(
                r"https?://(?:www\.)?.+", reason
            ):
                return await self.send_denied_embed(ctx, "You Can't Set AFK With Mentions Or Links In The Reason")

            embed = discord.Embed(
                description=f"**Choose Your AFK Type** {self.bot.emoji.AWAY}\n"
                f"> **Afk Ends**: {f'<t:{int(datetime.datetime.now().timestamp()+time)}:F>' if time else '`Never`'}\n"
                f"> **Reason**: {reason}",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            cancled = False

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                guild_afk = (
                    cache.afk.get("guilds", {})
                    .get(str(ctx.guild.id), {})
                    .get(str(ctx.author.id), {})
                )

                global_afk = cache.afk.get("global", {}).get(str(ctx.author.id), {})

                guild_afk_button = discord.ui.Button(
                    label="Guild AFK",
                    style=discord.ButtonStyle.gray,
                    row=0,
                    disabled=guild_afk.get("afk", False),
                )

                guild_afk_button.callback = lambda i: guild_afk_button_callback(i)

                global_afk_button = discord.ui.Button(
                    label="Global AFK",
                    style=discord.ButtonStyle.gray,
                    row=0,
                    disabled=global_afk.get("afk", False),
                )

                global_afk_button.callback = lambda i: global_afk_button_callback(i)

                cancle_button = discord.ui.Button(
                    label="Cancel", style=discord.ButtonStyle.gray, row=1
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(guild_afk_button)

                view.add_item(global_afk_button)

                # view.add_item(cancle_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def guild_afk_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Setting Guild AFK", color=0x2b2d31
                        ),
                        view=None,
                    )

                    nonlocal cancled

                    cancled = True

                    await storage.afk.delete(user_id=ctx.author.id)

                    data = await storage.afk.insert(
                        user_id=ctx.author.id,
                        guild_id=ctx.guild.id,
                        afk=True,
                        reason=reason,
                        afk_end=(
                            (
                                datetime.datetime.now(tz=datetime.timezone.utc)
                                + datetime.timedelta(seconds=time)
                            ).isoformat()
                            if time
                            else None
                        ),
                        created_at=datetime.datetime.now(
                            tz=datetime.timezone.utc
                        ).isoformat(),
                    )

                    try:

                        asyncio.create_task(afk_delay(self.bot, data))

                    except:

                        pass

                    afk_end_text = (
                        f" and will end at <t:{int(datetime.datetime.now().timestamp()+time)}:F>"
                        if time
                        else "."
                    )

                    await interaction.message.edit(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.SUCCESS} - Guild AFK Set{afk_end_text}",
                            color=0x2b2d31,
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def global_afk_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Setting Global AFK", color=0x2b2d31
                        ),
                        view=None,
                    )

                    nonlocal cancled

                    cancled = True

                    await storage.afk.delete(user_id=ctx.author.id)

                    data = await storage.afk.insert(
                        user_id=ctx.author.id,
                        guild_id=None,
                        afk=True,
                        reason=reason,
                        afk_end=(
                            (
                                datetime.datetime.now(tz=datetime.timezone.utc)
                                + datetime.timedelta(seconds=time)
                            ).isoformat()
                            if time
                            else None
                        ),
                        created_at=datetime.datetime.now(
                            tz=datetime.timezone.utc
                        ).isoformat(),
                    )

                    try:

                        asyncio.create_task(afk_delay(self.bot, data))

                    except:

                        pass

                    await interaction.message.edit(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.SUCCESS} - Global AFK Set{f' and Will End At <t:{int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()+time)}:F>' if time else '.'}",
                            color=0x2b2d31,
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=embed, view=await get_view())

            await asyncio.sleep(60)

            if not cancled:

                await message.edit(view=await get_view(True))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.group(name="prefix", help="Change The Bot's Prefix or Get The Current Prefix", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def prefix_group(self, ctx: commands.Context, new_prefix: str = None):
        if ctx.invoked_subcommand is None:
            if not new_prefix:
                cache_data = cache.guilds.get(str(ctx.guild.id)) or {}
                return await ctx.send(embed=discord.Embed(
                    description=f"**__Current Prefix:__** `{cache_data.get('prefix') or self.bot.BotConfig.PREFIX}`",
                    color=0x2b2d31
                ).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))
            
            await ctx.invoke(self.prefix_add, new_prefix=new_prefix)

    @prefix_group.command(name="add", help="Add a new prefix")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def prefix_add(self, ctx: commands.Context, new_prefix: str):
        if len(new_prefix) > 10:
            return await self.send_denied_embed(ctx, "The prefix can't be more than 10 characters.")
        
        cache_data = cache.guilds.get(str(ctx.guild.id))
        if not cache_data:
            await storage.guilds.insert(guild_id=ctx.guild.id)
            cache_data = cache.guilds.get(str(ctx.guild.id))
            
        await storage.guilds.update(id=cache_data.get("id"), prefix=new_prefix)
        await self.send_success_embed(ctx, f"Prefix changed to `{new_prefix}`")

    @prefix_group.command(name="remove", help="Remove the custom prefix (resets to default)")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def prefix_remove(self, ctx: commands.Context):
        cache_data = cache.guilds.get(str(ctx.guild.id))
        if not cache_data:
            await storage.guilds.insert(guild_id=ctx.guild.id)
            cache_data = cache.guilds.get(str(ctx.guild.id))
            
        await storage.guilds.update(id=cache_data.get("id"), prefix=self.bot.BotConfig.PREFIX)
        await self.send_success_embed(ctx, f"Prefix reset to `{self.bot.BotConfig.PREFIX}`")

    @prefix_group.command(name="reset", help="Reset the prefix to default")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def prefix_reset(self, ctx: commands.Context):
        await ctx.invoke(self.prefix_remove)

    @prefix_group.command(name="show", help="Show the current prefix")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def prefix_show(self, ctx: commands.Context):
        cache_data = cache.guilds.get(str(ctx.guild.id)) or {}
        await ctx.send(embed=discord.Embed(
            description=f"**__Current Prefix:__** `{cache_data.get('prefix') or self.bot.BotConfig.PREFIX}`",
            color=0x2b2d31
        ).set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url))

    @commands.hybrid_command(
        name="relationship",
        help="Set Your Relationship Status",
        with_app_command=True,
        aliases=["rs"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def relationship(self, ctx: commands.Context):

        try:

            available_relationships = {
                "single": self.bot.emoji.SINGLE,
                "married": self.bot.emoji.MARRIED,
                "engaged": self.bot.emoji.ENGAGED,
                "in_relationship": self.bot.emoji.IN_RELATIONSHIP,
                "complicated": self.bot.emoji.COMPLICATED,
            }

            user_data = cache.users.get(str(ctx.author.id), {})

            if not user_data:

                await storage.users.insert(user_id=ctx.author.id)

            async def get_embed():

                user_data = cache.users.get(str(ctx.author.id), {})

                embed = discord.Embed(
                    title="Relationship Status",
                    description=f"**__Current Relationship:__** `{user_data.get('relationship','single').capitalize()}`",
                    color=0x2b2d31,
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author.name}",
                    icon_url=ctx.author.display_avatar.url,
                )

                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                return embed

            timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled=False):

                user_data = cache.users.get(str(ctx.author.id), {})

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                select_relationship = discord.ui.Select(
                    placeholder="Select Your Relationship",
                    options=[
                        discord.SelectOption(
                            label=relationship.capitalize(),
                            value=relationship,
                            description=f"Set Your Relationship To {relationship.capitalize()}",
                            default=relationship
                            == user_data.get("relationship", "single"),
                        )
                        for relationship, emoji in available_relationships.items()
                    ],
                    row=0,
                )

                select_relationship.callback = lambda i: select_relationship_callback(i)

                view.add_item(select_relationship)

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.CANCLED,
                    row=1,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(cancle_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def select_relationship_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer()

                    user_data = cache.users.get(str(ctx.author.id), {})

                    await storage.users.update(
                        id=user_data.get("id"),
                        user_id=ctx.author.id,
                        relationship=interaction.data["values"][0],
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )


    @commands.hybrid_command(
        name="avatar",
        with_app_command=True,
        help="Display a user's avatar",
        aliases=["av"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def avatar(self, ctx, user: discord.Member = None):
        try:
            if ctx.interaction and not ctx.interaction.response:
                await ctx.defer()

            if not user:
                user = ctx.author

            member = None
            if isinstance(user, discord.Member):
                member = user
            else:
                try:
                    member = await ctx.guild.fetch_member(user.id)
                except:
                    pass

            avatar_url = user.display_avatar.url
            embed = discord.Embed(
                description=f"**{user.display_name}'s Avatar** {self.bot.emoji.MESSAGE}",
                color=user.color if user.color.value != 0 else 0x2b2d31
            )
            embed.set_image(url=avatar_url)
            embed.set_footer(
                text=f"Toxic (7ox4) • Requested by @{ctx.author.name}",
                icon_url=self.bot.user.display_avatar.url,
            )

            view = ProfileView(self.bot, ctx.author, user, member)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            logger.error(f"Error in avatar command: {e}")
            await ctx.send("An error occurred while processing the command.", delete_after=5)



    @commands.hybrid_group(
        name="banner",
        with_app_command=True,
        help="Display a user's banner",
        invoke_without_command=True,
        usage=["<user>", "server"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def banner(self, ctx, user: discord.Member = None):
        try:
            if ctx.interaction and not ctx.interaction.response:
                await ctx.defer()

            if not user:
                user = ctx.author

            member = None
            if isinstance(user, discord.Member):
                member = user
            else:
                try:
                    member = await ctx.guild.fetch_member(user.id)
                except:
                    pass

            fetched_user = await self.bot.fetch_user(user.id)
            if not fetched_user.banner:
                embed = discord.Embed(
                    description=f"**{user.display_name}** has no global banner {self.bot.emoji.ERROR}",
                    color=0x2b2d31,
                )
                view = ProfileView(self.bot, ctx.author, user, member)
                return await ctx.send(embed=embed, view=view)

            banner_url = fetched_user.banner.url
            embed = discord.Embed(
                description=f"**{user.display_name}'s Banner** {self.bot.emoji.LOG}",
                color=user.color if user.color.value != 0 else 0x2b2d31
            )
            embed.set_image(url=banner_url)
            embed.set_footer(
                text=f"Toxic (7ox4) • Requested by @{ctx.author.name}",
                icon_url=self.bot.user.display_avatar.url,
            )

            view = ProfileView(self.bot, ctx.author, user, member)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            logger.error(f"Error in banner command: {e}")
            await ctx.send("An error occurred while processing the command.", delete_after=5)

    @banner.command(
        name="server",
        help="Display the server's banner",
        aliases=["guild"],
    )
    async def banner_server(self, ctx):

        try:

            if ctx.interaction and not ctx.interaction.response:

                await ctx.defer()

            guild = await self.bot.fetch_guild(ctx.guild.id)

            if not guild.banner:

                embed = discord.Embed(
                    description=f"This Server doesn't have a banner.", color=0x2b2d31
                )

                await ctx.send(embed=embed)

                return

            banner_url = guild.banner.url

            embed = discord.Embed(
                description=f"**{guild.name}'s Banner** {self.bot.emoji.GUILD}",
                color=0x2b2d31
            )
            embed.set_image(url=banner_url)
            embed.set_footer(
                text=f"Toxic (7ox4) • Requested by @{ctx.author.name}",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in banner command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.group(
        name="list",
        help="different list commands",
        aliases=["ls"],
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list(self, ctx: commands.Context):

        embed = discord.Embed(
            title="List Commands",
            color=0x2b2d31,
            description="List of all the list commands\n\n",
        )

        if hasattr(ctx.command, "commands"):

            for command in ctx.command.commands:

                embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command} {command.name}`** : {command.help}\n"

        await ctx.send(embed=embed)

    @list.command(name="emojis", help="List all the emojis in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_emojis(self, ctx: commands.Context):

        try:

            emojis = ctx.guild.emojis

            if not emojis:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no emojis in this server",
                        color=0x2b2d31,
                    )
                )

            # make 5 by 5 grid of emojis

            emojis = [emojis[i : i + 10] for i in range(0, len(emojis), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Emojis",
                    color=0x2b2d31,
                    description="",
                )

                for emoji in emojis[current_page_index]:

                    embed.description += f"> - {emoji} - `{emoji.id}`\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(emojis)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(emojis) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="channels", help="List all the channels in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_channels(self, ctx: commands.Context):

        try:

            channels = ctx.guild.channels

            # make 5 by 5 grid of channels

            if not channels:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no channels in this server",
                        color=0x2b2d31,
                    )
                )

            channels = [channels[i : i + 10] for i in range(0, len(channels), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Channels",
                    color=0x2b2d31,
                    description="",
                )

                for channel in channels[current_page_index]:

                    embed.description += f"> - {channel.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(channels)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(channels) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="bots", help="List all the bots in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_bots(self, ctx: commands.Context):

        try:

            bots = [member for member in ctx.guild.members if member.bot]

            if not bots:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no bots in this server", color=0x2b2d31
                    )
                )

            # make 5 by 5 grid of bots

            bots = [bots[i : i + 10] for i in range(0, len(bots), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Bots", color=0x2b2d31, description=""
                )

                for bot in bots[current_page_index]:

                    embed.description += f"> - {bot.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(bots)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(bots) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="admins", help="List all the admins in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_admins(self, ctx: commands.Context):

        try:

            admins = [
                member
                for member in ctx.guild.members
                if member.guild_permissions.administrator and not member.bot
            ]

            if not admins:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no admins in this server",
                        color=0x2b2d31,
                    )
                )

            # make 5 by 5 grid of admins

            admins = [admins[i : i + 10] for i in range(0, len(admins), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Admins",
                    color=0x2b2d31,
                    description="",
                )

                for admin in admins[current_page_index]:

                    embed.description += f"> - {admin.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(admins)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(admins) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="bans", help="List all the bans in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_bans(self, ctx: commands.Context):

        try:

            bans = []

            async for ban in ctx.guild.bans(limit=None):

                bans.append(ban.user)

            if not bans:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no bans in this server", color=0x2b2d31
                    )
                )

            # make 5 by 5 grid of bans

            bans = [bans[i : i + 10] for i in range(0, len(bans), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Bans", color=0x2b2d31, description=""
                )

                for ban in bans[current_page_index]:

                    embed.description += f"> - {ban.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(bans)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(bans) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="roles", help="List all the roles in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_roles(self, ctx: commands.Context):

        try:

            roles = ctx.guild.roles

            if not roles:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no roles in this server", color=0x2b2d31
                    )
                )

            # make 5 by 5 grid of roles

            roles = [roles[i : i + 10] for i in range(0, len(roles), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Roles", color=0x2b2d31, description=""
                )

                for role in roles[current_page_index]:

                    embed.description += f"> - {role.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(roles)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(roles) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="boosters", help="List all the boosters in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_boosters(self, ctx: commands.Context):

        try:

            boosters = ctx.guild.premium_subscribers

            if not boosters:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no boosters in this server",
                        color=0x2b2d31,
                    )
                )

            # make 5 by 5 grid of boosters

            boosters = [boosters[i : i + 10] for i in range(0, len(boosters), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Boosters",
                    color=0x2b2d31,
                    description="",
                )

                for booster in boosters[current_page_index]:

                    embed.description += f"> - {booster.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(boosters)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(boosters) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="inrole", help="List all the members in a role")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_inrole(self, ctx: commands.Context, role: discord.Role):

        try:

            members = role.members

            if not members:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"There are no members in the {role.mention} role",
                        color=0x2b2d31,
                    )
                )

            # make 5 by 5 grid of members

            members = [members[i : i + 10] for i in range(0, len(members), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"Members in the {role.name} role",
                    color=0x2b2d31,
                    description="",
                )

                i = 1

                for member in members[current_page_index]:

                    embed.description += f"{i} • {member.mention} - `{member.id}`\n"

                    i += 1

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(members)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                if len(members) == 1:

                    nonlocal cancled

                    cancled = True

                    return None

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(members) - 1,
                )

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(stop_button)

                view.add_item(next_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(name="uptime", help="Get the uptime of the bot")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def uptime(self, ctx: commands.Context):

        try:

            uptime = (
                datetime.datetime.now(tz=datetime.timezone.utc) - self.bot.start_time
            ).total_seconds()

            # convert the uptime to days, hours, minutes and seconds

            uptime_text = ""

            if uptime >= 86400:

                uptime_text += f"{int(uptime/86400)}d "

                uptime %= 86400

            if uptime >= 3600:

                uptime_text += f"{int(uptime/3600)}h "

                uptime %= 3600

            if uptime >= 60:

                uptime_text += f"{int(uptime/60)}m "

                uptime %= 60

            uptime_text += f"{int(uptime)}s"

            await ctx.send(
                embed=discord.Embed(
                    title="Uptime",
                    color=0x2b2d31,
                    description=f"```\n{uptime_text}```",
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(name="roleicon", help="Set a role icon", aliases=["roleemoji"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def roleicon(
        self, ctx: commands.Context, role: discord.Role, emoji: discord.PartialEmoji
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "manage_roles"):

                return

            if not await checks.check_if_user_can_manage_this_role(ctx, role):

                return

            if ctx.guild.premium_tier < 2:

                return await ctx.send(
                    embed=discord.Embed(
                        description="You need to have server boost level 2 to use this command",
                        color=0x2b2d31,
                    )
                )

            try:

                def get_image_byte_by_url(url):

                    return requests.get(url).content

                await role.edit(display_icon=get_image_byte_by_url(emoji.url))

                await ctx.send(
                    embed=discord.Embed(
                        description=f"Role icon for {role.mention} has been Changed",
                        color=0x2b2d31,
                    ).set_image(
                        url=role.display_icon.url if role.display_icon else None
                    )
                )

            except discord.HTTPException as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occurred while setting the role icon for {role.mention}",
                        color=0x2b2d31,
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="serverinfo",
        help="Get information about the server",
        aliases=["guildinfo", "si", "gi"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        created_at = int(guild.created_at.timestamp())
        
        embed = discord.Embed(
            description=(
                f"**{guild.name} Information** {self.bot.emoji.GUILD}\n"
                f"Established on <t:{created_at}:F> (<t:{created_at}:R>)\n\n"
                f"<a:neo_Crown:1498047758509150379> **Owner:** {guild.owner.mention} (`{guild.owner.id}`)\n"
                f"{self.bot.emoji.GUILD} **Server ID:** `{guild.id}`\n"
                f"{self.bot.emoji.PREMIUM} **Boost Status:** Level {guild.premium_tier} ({guild.premium_subscription_count} Boosts)"
            ),
            color=0x2b2d31
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        humans = len([m for m in guild.members if not m.bot])
        bots = guild.member_count - humans
        
        members_info = (
            f">>> **Total:** `{guild.member_count}`\n"
            f"**Humans:** `{humans}`\n"
            f"**Bots:** `{bots}`"
        )
        embed.add_field(name=f"{self.bot.emoji.MEMBER} Members", value=members_info, inline=True)

        channels_info = (
            f">>> **Text:** `{len(guild.text_channels)}`\n"
            f"**Voice:** `{len(guild.voice_channels)}`\n"
            f"**Categories:** `{len(guild.categories)}`"
        )
        embed.add_field(name=f"{self.bot.emoji.CHANNEL} Channels", value=channels_info, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        mfa_level = "Required" if guild.mfa_level == 1 else "None"
        security_info = (
            f">>> **Verification:** `{guild.verification_level.name.capitalize()}`\n"
            f"**MFA Requirement:** `{mfa_level}`\n"
            f"**Content Filter:** `{guild.explicit_content_filter.name.capitalize().replace('_', ' ')}`"
        )
        embed.add_field(name=f"{self.bot.emoji.SECURITY} Security", value=security_info, inline=True)
        
        extras_info = (
            f">>> **Roles:** `{len(guild.roles)}`\n"
            f"**Emojis:** `{len(guild.emojis)}`\n"
            f"**Stickers:** `{len(guild.stickers)}`"
        )
        embed.add_field(name=f"{self.bot.emoji.INFO} Extras", value=extras_info, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="userinfo",
        help="Get information about a user",
        aliases=["ui", "whois"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def userinfo(self, ctx: commands.Context, user: discord.Member = None):
        try:
            if not user:
                user = ctx.author
            
            # Fetch full user for banner
            fetched_user = await self.bot.fetch_user(user.id)
            
            # General Info
            name = f"{user.name}"
            user_id = f"{user.id}"
            nickname = user.nick if user.nick else "None"
            is_bot = "Yes" if user.bot else "No"
            created_at = f"<t:{int(user.created_at.timestamp())}:R>"
            joined_at = f"<t:{int(user.joined_at.timestamp())}:R>"
            
            # Roles
            top_role = user.top_role.mention if len(user.roles) > 1 else "None"
            total_roles = len(user.roles) - 1 # Subtracting @everyone
            
            # Extras
            boosting = f"Boosting since <t:{int(user.premium_since.timestamp())}:R>" if user.premium_since else "Not Boosting"
            voice_status = f"{user.voice.channel.name}" if user.voice and user.voice.channel else "None"
            
            # Key Permissions
            perms = []
            if user.guild_permissions.administrator: perms.append("Administrator")
            if user.guild_permissions.kick_members: perms.append("Kick Members")
            if user.guild_permissions.ban_members: perms.append("Ban Members")
            if user.guild_permissions.manage_channels: perms.append("Manage Channels")
            if user.guild_permissions.manage_guild: perms.append("Manage Guild")
            if user.guild_permissions.manage_messages: perms.append("Manage Messages")
            if user.guild_permissions.manage_roles: perms.append("Manage Roles")
            if user.guild_permissions.mention_everyone: perms.append("Mention Everyone")
            if user.guild_permissions.manage_nicknames: perms.append("Manage Nicknames")
            if user.guild_permissions.manage_webhooks: perms.append("Manage Webhooks")
            
            perm_text = ", ".join(perms) if perms else "None"
            
            # Acknowledgement
            ack = "User"
            if user.guild_permissions.administrator: ack = "Administrator"
            if user.id == ctx.guild.owner_id: ack = "Server Owner"
            if user.id in self.bot.users_data.root: ack = "Real Owner"

            embed = discord.Embed(
                description=(
                    f"**{user.display_name} Information** {self.bot.emoji.MEMBER}\n"
                    f"Detailed analysis of {user.mention} within this guild context.\n\n"
                    f"**__Account History__**\n"
                    f"> **Created:** {created_at}\n"
                    f"> **Joined:** {joined_at}"
                ),
                color=user.color if user.color.value != 0 else 0x2b2d31
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            embed.add_field(
                name=f"{self.bot.emoji.SEARCH} General",
                value=f"**Name :** {name}\n**ID :** {user_id}\n**Nickname :** {nickname}\n**Is Bot :** {is_bot}",
                inline=False
            )
            
            embed.add_field(
                name=f"{self.bot.emoji.ROLE} Roles",
                value=f"**Top Role :** {top_role}\n**Total Roles :** {total_roles}",
                inline=False
            )
            
            embed.add_field(
                name=f"{self.bot.emoji.EXTRA} Extras",
                value=f"**Boosting :** {boosting}\n**Voice :** {self.bot.emoji.MICROPHONE if user.voice else ''} {voice_status}",
                inline=False
            )
            
            embed.add_field(
                name=f"{self.bot.emoji.SECURITY} Key Perms",
                value=f"```\n{perm_text}```",
                inline=False
            )
            
            embed.add_field(
                name=f"{self.bot.emoji.ROOT} Acknowledgement",
                value=f"```\n{ack}```",
                inline=False
            )

            # NPR Status
            user_cache = self.bot.cache.users.get(str(user.id), {})
            has_npr = user_cache.get('no_prefix', False) or user_cache.get('no_prefix_subscription', False)
            
            if has_npr:
                no_prefix_end = user_cache.get('no_prefix_end')
                if no_prefix_end:
                    try:
                        if isinstance(no_prefix_end, str):
                            expire_at = datetime.datetime.fromisoformat(no_prefix_end)
                        else:
                            expire_at = no_prefix_end
                        
                        if expire_at.astimezone() > datetime.datetime.now().astimezone():
                            npr_text = f"Premium (Expires <t:{int(expire_at.timestamp())}:R>)"
                            embed.add_field(
                                name=f"<a:premium_avon:1498201608985514125> NPR Status",
                                value=f"**{npr_text}**",
                                inline=False
                            )
                    except:
                        pass
                else:
                    embed.add_field(
                        name=f"<a:premium_avon:1498201608985514125> NPR Status",
                        value=f"**Permanent**",
                        inline=False
                    )
            
            if fetched_user.banner:
                embed.set_image(url=fetched_user.banner.url)
                
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in userinfo command: {e}")
            await ctx.send("An error occurred while processing the command.", delete_after=5)

    @commands.command(
        name="roleinfo", help="Get information about a role", aliases=["ri"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):

        try:

            embed = discord.Embed(
                description=f"**{role.name} Information** {self.bot.emoji.ROLE}\n> **ID:** `{role.id}`\n> **Created:** <t:{int(role.created_at.timestamp())}:F>",
                color=role.color
            )

            embed.add_field(
                name=f"{self.bot.emoji.GENERAL} __General info__",
                value=f"""> **{self.bot.emoji.NAME} Name:** {role.mention}






> {self.bot.emoji.ID} Id: `{role.id}`






> {self.bot.emoji.POSITION} Position: `{role.position}`






> {self.bot.emoji.MENTIONABLE} Mentionable: {self.bot.emoji.YES if role.mentionable else self.bot.emoji.NO}






> {self.bot.emoji.HOIST} Hoist: {self.bot.emoji.YES if role.hoist else self.bot.emoji.NO}






> {self.bot.emoji.MANAGED} Managed By Bot: {self.bot.emoji.YES if role.managed else self.bot.emoji.NO}






> {self.bot.emoji.COLOR} Color: `{role.color}`






> {self.bot.emoji.MEMBERS} Members: `{len(role.members)}`






> {self.bot.emoji.CREATED} Created At: <t:{int(role.created_at.timestamp())}:F>""",
                inline=False,
            )

            embed.add_field(
                name=f"{self.bot.emoji.PERMISSIONS} __Permissions__",
                value=(
                    "```\n"
                    + (
                        "Administrator"
                        if role.permissions.administrator
                        else (
                            " | ".join(
                                [perm for perm, value in role.permissions if value]
                            )
                            if len([perm for perm, value in role.permissions if value])
                            < 25
                            else " | ".join(
                                [perm for perm, value in role.permissions if value][:25]
                            )
                            + f" and {len([perm for perm, value in role.permissions if value]) - 25} more"
                        )
                    )
                    + "```"
                    if role.permissions
                    else "No Permissions"
                ),
                inline=False,
            )

            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.hybrid_command(
        name="membercount",
        help="Get the member count of the server",
        aliases=["mc"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def membercount(self, ctx: commands.Context):

        try:
            embed = discord.Embed(
                description=(
                    f"**Member Count** {self.bot.emoji.MEMBER}\n"
                    f"> **Total:** `{ctx.guild.member_count}`\n"
                    f"> **Humans:** `{len([m for m in ctx.guild.members if not m.bot])}`\n"
                    f"> **Bots:** `{len([m for m in ctx.guild.members if m.bot])}`"
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.group(name="banner", invoke_without_command=True)
    async def banner(self, ctx: commands.Context, *, user: discord.Member = None):
        user = user or ctx.author
        if not user.banner:
            return await self.send_denied_embed(ctx, f"{user.mention} does not have a banner.")
        embed = discord.Embed(title=f"{user.name}'s Banner", color=0x2b2d31)
        embed.set_image(url=user.banner.url)
        await ctx.send(embed=embed)

    @banner.command(name="server")
    async def banner_server(self, ctx: commands.Context):
        if not ctx.guild.banner:
            return await self.send_denied_embed(ctx, "This server does not have a banner.")
        embed = discord.Embed(title=f"{ctx.guild.name}'s Banner", color=0x2b2d31)
        embed.set_image(url=ctx.guild.banner.url)
        await ctx.send(embed=embed)

    @commands.command(
        name="firstmessage", help="Get the first message of a channel", aliases=["fm"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def firstmessage(
        self, ctx: commands.Context, channel: discord.TextChannel = None
    ):

        try:

            if not channel:

                channel = ctx.channel

            first_message = None

            async for message in channel.history(limit=1, oldest_first=True):

                first_message = message

            if not first_message:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"No messages found in {channel.mention}",
                        color=0x2b2d31,
                    )
                )

            embed = discord.Embed(
                description=f"First message found in {channel.mention}",
                color=0x2b2d31,
            )

            view = discord.ui.View()

            message_url_button = discord.ui.Button(
                style=discord.ButtonStyle.url,
                label="Click to View",
                url=first_message.jump_url,
            )

            view.add_item(message_url_button)

            await ctx.send(embed=embed, view=view)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )


    @commands.hybrid_command(
        name="boostcount",
        aliases=["bc", "boostinfo"],
        with_app_command=True,
        help="Get The Server's Boost Count and Level",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def boostcount_command(self, ctx: commands.Context):
        try:
            guild = ctx.guild
            boost_count = guild.premium_subscription_count
            boost_level = guild.premium_tier
            
            embed = discord.Embed(
                title="Boost Info !",
                description=f"⤷ The server Boost Level is **{boost_level}** with **{boost_count}** Boosts",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Command: boostcount, Error: {e}")
            await ctx.send("An Error Occurred While Fetching The Boost Info")

    @commands.command(name="remind", help="Set a reminder for yourself", aliases=["reminder", "remindme"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def remind(self, ctx: commands.Context, time_str: str, *, task: str):
        try:
            # Simple time parser (e.g. 10m, 1h, 5s)
            time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            unit = time_str[-1].lower()
            if unit not in time_units:
                return await self.send_denied_embed(ctx, "Invalid time format! Use `s`, `m`, `h`, or `d` (e.g. `10m`).")
            
            try:
                seconds = int(time_str[:-1]) * time_units[unit]
            except ValueError:
                return await self.send_denied_embed(ctx, "Invalid time number! (e.g. `10m`).")

            if seconds > 86400 * 30: # 30 days limit
                return await self.send_denied_embed(ctx, "Reminders cannot exceed 30 days.")

            await self.send_success_embed(ctx, f"I will remind you about **{task}** in **{time_str}**.")
            
            await asyncio.sleep(seconds)
            
            try:
                embed = discord.Embed(
                    description=f"**Reminder Reminder** {self.bot.emoji.BOT}\n{ctx.author.mention}, you asked to be reminded about:\n\n**{task}**",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Elara Reminders", icon_url=self.bot.user.display_avatar.url)
                await ctx.author.send(embed=embed)
            except:
                await ctx.send(f"{ctx.author.mention}, here is your reminder: **{task}**")

        except Exception as e:
            logger.error(f"Error in remind: {e}")
            await self.send_denied_embed(ctx, "An error occurred while setting your reminder.")

    @commands.command(name="quote", help="Get an inspirational quote")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def quote(self, ctx: commands.Context):
        try:
            response = requests.get("https://zenquotes.io/api/random")
            if response.status_code == 200:
                data = response.json()[0]
                quote_text = data['q']
                author = data['a']
                
                embed = discord.Embed(
                    description=f"**Daily Inspiration** {self.bot.emoji.BOT}\n\"{quote_text}\"\n\n- **{author}**",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Wisdom", icon_url=self.bot.user.display_avatar.url)
                await ctx.send(embed=embed)
            else:
                await self.send_denied_embed(ctx, "Failed to fetch a quote. Try again later!")
        except Exception as e:
            logger.error(f"Error in quote: {e}")
            await self.send_denied_embed(ctx, "An error occurred while fetching the quote.")

    @commands.command(name="fact", help="Get a random interesting fact")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def fact(self, ctx: commands.Context):
        try:
            response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
            if response.status_code == 200:
                data = response.json()
                fact_text = data['text']
                
                embed = discord.Embed(
                    description=f"**Interesting Fact** {self.bot.emoji.INFO}\n{fact_text}",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Knowledge", icon_url=self.bot.user.display_avatar.url)
                await ctx.send(embed=embed)
            else:
                await self.send_denied_embed(ctx, "Failed to fetch a fact. Try again later!")
        except Exception as e:
            logger.error(f"Error in fact: {e}")
            await self.send_denied_embed(ctx, "An error occurred while fetching the fact.")


    def format_stat_duration(self, seconds):
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    @commands.hybrid_command(
        name="messages",
        aliases=["m", "msg"],
        with_app_command=True,
        help="Check your message statistics in the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
    async def messages_command(self, ctx, user: discord.Member = None):
        try:
            if not user:
                user = ctx.author

            stats = await storage.member_stats.get(user_id=user.id, guild_id=ctx.guild.id)
            if not stats:
                stats = {
                    'messages_all_time': 0,
                    'messages_weekly': 0,
                    'messages_daily': 0
                }

            embed = discord.Embed(
                description=f"**{user.display_name}'s Messages** {self.bot.emoji.MESSAGE}\n\n"
                            f"**All time {self.bot.emoji.NEXT} {stats.get('messages_all_time', 0)}** messages in this server\n"
                            f"**Weekly {self.bot.emoji.NEXT} {stats.get('messages_weekly', 0)}** messages in this server\n"
                            f"**Today {self.bot.emoji.NEXT} {stats.get('messages_daily', 0)}** messages in this server\n\n"
                            f"{self.bot.emoji.LOADING} Messages are being updated in real-time",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in messages command: {e}")
            await ctx.send("An error occurred while fetching message stats.", delete_after=5)

    @commands.hybrid_command(
        name="invites",
        aliases=["i", "inv"],
        with_app_command=True,
        help="Check your invite statistics in the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
    async def invites_command(self, ctx, user: discord.Member = None):
        try:
            if not user:
                user = ctx.author

            stats = await storage.member_stats.get(user_id=user.id, guild_id=ctx.guild.id)
            if not stats:
                stats = {}

            def gs(field): return stats.get(field, 0)

            total = gs('invites_total')
            regular = gs('invites_regular')
            fake = gs('invites_fake')
            leaves = gs('invites_leaves')

            embed = discord.Embed(
                description=f"**{user.display_name}'s Invites** {self.bot.emoji.INVITE}\n\n"
                            f"{user.display_name} has a total of **{total}** invites!\n\n"
                            f"{self.bot.emoji.NEXT} Regular: **{regular}**\n"
                            f"{self.bot.emoji.NEXT} Fake: **{fake}**\n"
                            f"{self.bot.emoji.NEXT} Leaves: **{leaves}**\n\n"
                            f"{self.bot.emoji.LOADING} Invites update in real-time",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in invites command: {e}")
            await ctx.send("An error occurred while fetching invite stats.", delete_after=5)

    @commands.hybrid_command(
        name="voicestats",
        aliases=["vc", "vstats"],
        with_app_command=True,
        help="Check your voice statistics in the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
    async def voice_command(self, ctx, user: discord.Member = None):
        try:
            if not user:
                user = ctx.author

            stats = await storage.member_stats.get(user_id=user.id, guild_id=ctx.guild.id) or {}
            current_session_duration = 0
            voice_cog = self.bot.get_cog("on_voice_state_update")
            if voice_cog and (user.id, ctx.guild.id) in voice_cog.voice_tracking:
                data = voice_cog.voice_tracking[(user.id, ctx.guild.id)]
                now = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
                current_session_duration = int(now - data['last_update'])

            def gs(field):
                val = stats.get(field, 0)
                if field in ['voice_all_time', 'voice_weekly', 'voice_daily']:
                    val += current_session_duration
                elif field in ['voice_muted_all_time', 'voice_muted_weekly', 'voice_muted_daily'] and voice_cog and (user.id, ctx.guild.id) in voice_cog.voice_tracking and voice_cog.voice_tracking[(user.id, ctx.guild.id)]['muted']:
                    val += current_session_duration
                elif field in ['voice_deafened_all_time', 'voice_deafened_weekly', 'voice_deafened_daily'] and voice_cog and (user.id, ctx.guild.id) in voice_cog.voice_tracking and voice_cog.voice_tracking[(user.id, ctx.guild.id)]['deafened']:
                    val += current_session_duration
                elif field in ['voice_afk_all_time', 'voice_afk_weekly', 'voice_afk_daily'] and voice_cog and (user.id, ctx.guild.id) in voice_cog.voice_tracking and voice_cog.voice_tracking[(user.id, ctx.guild.id)]['afk']:
                    val += current_session_duration
                return val

            total_all = gs('voice_all_time')
            
            embed = discord.Embed(
                description=f"**{user.display_name}'s Voice Stats** {self.bot.emoji.MUSIC}\n\n"
                            f"{user.display_name} spent a total of **{self.format_stat_duration(total_all)}** in voice channels!\n\n"
                            f"**All Time Breakdown:**\n"
                            f"{self.bot.emoji.TIME} Muted: **{self.format_stat_duration(gs('voice_muted_all_time'))}**\n"
                            f"{self.bot.emoji.TIME} Deafened: **{self.format_stat_duration(gs('voice_deafened_all_time'))}**\n"
                            f"{self.bot.emoji.TIME} AFK: **{self.format_stat_duration(gs('voice_afk_all_time'))}**\n\n"
                            f"**Daily Breakdown:**\n"
                            f"{self.bot.emoji.TIME} Total: **{self.format_stat_duration(gs('voice_daily'))}**\n"
                            f"{self.bot.emoji.TIME} Muted: **{self.format_stat_duration(gs('voice_muted_daily'))}**\n"
                            f"{self.bot.emoji.TIME} Deafened: **{self.format_stat_duration(gs('voice_deafened_daily'))}**\n"
                            f"{self.bot.emoji.TIME} AFK: **{self.format_stat_duration(gs('voice_afk_daily'))}**\n\n"
                            f"**Weekly Breakdown:**\n"
                            f"{self.bot.emoji.TIME} Total: **{self.format_stat_duration(gs('voice_weekly'))}**\n"
                            f"{self.bot.emoji.TIME} Muted: **{self.format_stat_duration(gs('voice_muted_weekly'))}**\n"
                            f"{self.bot.emoji.TIME} Deafened: **{self.format_stat_duration(gs('voice_deafened_weekly'))}**\n"
                            f"{self.bot.emoji.TIME} AFK: **{self.format_stat_duration(gs('voice_afk_weekly'))}**\n\n"
                            f"{self.bot.emoji.LOADING} Voice stats update in real time",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in voice command: {e}")
            await ctx.send("An error occurred while fetching voice stats.", delete_after=5)

    @commands.group(
        name="lb",
        aliases=["leaderboard"],
        invoke_without_command=True,
        help="Check the server leaderboards"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
    async def lb_group(self, ctx):
        embed = discord.Embed(
            description=(
                f"**Leaderboard Suite** {self.bot.emoji.LOG}\n"
                f"Select a category to view the top contributors!\n\n"
                f"{self.bot.emoji.CATEGORY} • `{ctx.prefix}lb messages` - View message rankings\n"
                f"{self.bot.emoji.CATEGORY} • `{ctx.prefix}lb voice` - View voice activity rankings\n"
                f"{self.bot.emoji.CATEGORY} • `{ctx.prefix}lb invites` - View invitation rankings"
            ),
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @lb_group.command(name="messages", aliases=["msg", "m"])
    async def lb_messages(self, ctx):
        await self._send_leaderboard(ctx, "messages_all_time", "Message Leaderboard (All Time)")

    @lb_group.command(name="voice", aliases=["vc", "v"])
    async def lb_voice(self, ctx):
        await self._send_leaderboard(ctx, "voice_all_time", "Voice Leaderboard (All Time)", is_voice=True)

    @lb_group.command(name="invites", aliases=["inv", "i"])
    async def lb_invites(self, ctx):
        await self._send_leaderboard(ctx, "invites_total", "Invite Leaderboard")

    @commands.group(
        name="mlb",
        aliases=["messagesleaderboard", "msglb"],
        invoke_without_command=True,
        help="Check the message leaderboard for this server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
    async def mlb(self, ctx):
        await self.mlb_alltime(ctx)

    @mlb.command(name="alltime", aliases=["all"])
    async def mlb_alltime(self, ctx):
        await self._send_leaderboard(ctx, "messages_all_time", "Message Leaderboard (All Time)")

    @mlb.command(name="weekly", aliases=["week"])
    async def mlb_weekly(self, ctx):
        await self._send_leaderboard(ctx, "messages_weekly", "Message Leaderboard (Weekly)")

    @mlb.command(name="daily", aliases=["today", "day"])
    async def mlb_daily(self, ctx):
        await self._send_leaderboard(ctx, "messages_daily", "Message Leaderboard (Today)")

    @commands.group(
        name="vlb",
        aliases=["voiceleaderboard", "vclb"],
        invoke_without_command=True,
        help="Check the voice leaderboard for this server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
    async def vlb(self, ctx):
        await self.vlb_alltime(ctx)

    @vlb.command(name="alltime", aliases=["all"])
    async def vlb_alltime(self, ctx):
        await self._send_leaderboard(ctx, "voice_all_time", "Voice Leaderboard (All Time)", is_voice=True)

    @vlb.command(name="weekly", aliases=["week"])
    async def vlb_weekly(self, ctx):
        await self._send_leaderboard(ctx, "voice_weekly", "Voice Leaderboard (Weekly)", is_voice=True)

    @vlb.command(name="daily", aliases=["today", "day"])
    async def vlb_daily(self, ctx):
        await self._send_leaderboard(ctx, "voice_daily", "Voice Leaderboard (Today)", is_voice=True)

    @commands.command(name="resetm", help="Reset message stats for a user or the entire guild")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def resetm(self, ctx, target: str = None):
        try:
            if not target:
                return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} Please specify a user or use `{ctx.prefix}resetm all`", color=color.red))

            if target.lower() == "all":
                await storage.member_stats.reset_guild_stats(ctx.guild.id, "messages")
                embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} Clinically reset **all message stats** for this server.", color=color.green)
            else:
                try:
                    user = await commands.MemberConverter().convert(ctx, target)
                    await storage.member_stats.reset_user_stats(user.id, ctx.guild.id, "messages")
                    embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} Clinically reset message stats for **{user.mention}**.", color=color.green)
                except commands.MemberNotFound:
                    return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} User not found.", color=color.red))

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in resetm: {e}")

    @commands.command(name="resetvc", help="Reset voice stats for a user or the entire guild")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def resetvc(self, ctx, target: str = None):
        try:
            if not target:
                return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} Please specify a user or use `{ctx.prefix}resetvc all`", color=color.red))

            if target.lower() == "all":
                await storage.member_stats.reset_guild_stats(ctx.guild.id, "voice")
                embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} Clinically reset **all voice stats** for this server.", color=color.green)
            else:
                try:
                    user = await commands.MemberConverter().convert(ctx, target)
                    await storage.member_stats.reset_user_stats(user.id, ctx.guild.id, "voice")
                    embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} Clinically reset voice stats for **{user.mention}**.", color=color.green)
                except commands.MemberNotFound:
                    return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} User not found.", color=color.red))

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in resetvc: {e}")

    @commands.command(name="reseti", help="Reset invite stats for a user or the entire guild")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def reseti(self, ctx, target: str = None):
        try:
            if not target:
                return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} Please specify a user or use `{ctx.prefix}reseti all`", color=color.red))

            if target.lower() == "all":
                await storage.member_stats.reset_guild_stats(ctx.guild.id, "invites")
                embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} Clinically reset **all invite stats** for this server.", color=color.green)
            else:
                try:
                    user = await commands.MemberConverter().convert(ctx, target)
                    await storage.member_stats.reset_user_stats(user.id, ctx.guild.id, "invites")
                    embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} Clinically reset invite stats for **{user.mention}**.", color=color.green)
                except commands.MemberNotFound:
                    return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} User not found.", color=color.red))

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in reseti: {e}")

    async def _send_leaderboard(self, ctx, field, title, is_voice=False):
        try:
            top_users = await storage.member_stats.get_top(ctx.guild.id, field, limit=10)
            
            if not top_users:
                return await ctx.send(embed=discord.Embed(description=f"**No data found for this leaderboard.**", color=0x2b2d31))

            description = f"**{title}** {self.bot.emoji.LOG}\n\n"
            
            for i, user_data in enumerate(top_users, 1):
                user_id = user_data.get('user_id')
                user = ctx.guild.get_member(user_id)
                name = user.display_name if user else f"User({user_id})"
                value = user_data.get(field, 0)
                
                if is_voice:
                    formatted_value = self.format_stat_duration(value)
                elif "invites" in field:
                    formatted_value = f"**{value}** invites"
                else:
                    formatted_value = f"**{value}** msgs"
                    
                description += f"**{i}.** {name} {self.bot.emoji.NEXT} {formatted_value}\n"

            description += f"\n-# Leaderboard updates in real-time"
            embed = discord.Embed(description=description, color=0x2b2d31)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in leaderboard: {e}")
            await ctx.send("An error occurred while fetching the leaderboard.", delete_after=5)

    @commands.command(name="servericon", help="Display the server's icon", aliases=["sicon"])
    @checks.ignore_check()
    @checks.blacklist_check()
    async def servericon(self, ctx):
        if not ctx.guild.icon:
            return await self.send_denied_embed(ctx, "This server has no icon.")
        
        embed = discord.Embed(
            description=f"**{ctx.guild.name}'s Icon** {self.bot.emoji.GUILD}",
            color=0x2b2d31
        )
        embed.set_image(url=ctx.guild.icon.url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="about", help="Display information about the bot")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def about(self, ctx):
        embed = discord.Embed(
            description=(
                f"**About Elara** {self.bot.emoji.BOT}\n"
                f"Developed by **Toxic (7ox4)**, Elara is a multi-purpose bot designed for speed, stability, and aesthetic excellence.\n\n"
                f"{self.bot.emoji.INFO} **Bot Statistics**\n"
                f"> **Servers:** `{len(self.bot.guilds)}` Servers\n"
                f"> **Users:** `{sum(g.member_count for g in self.bot.guilds)}` Total Users\n"
                f"> **Latency:** `{round(self.bot.latency * 1000)}ms` Heartbeat\n"
                f"> **Uptime:** `{str(datetime.timedelta(seconds=int(time.time() - self.bot.start_time)))}` Elapsed\n\n"
                f"{self.bot.emoji.LINK} **Official Links**\n"
                f"> [Invite]({self.bot.urls.INVITE}) • [Support]({self.bot.urls.SUPPORT}) • [Website]({self.bot.urls.WEBSITE})"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))
