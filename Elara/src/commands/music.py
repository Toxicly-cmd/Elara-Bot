from __future__ import annotations
from typing import Union, Optional, Any
import discord


from discord.ext import commands


import wavelink


import Elara.src.checks.checks as checks


import storage.guilds


import storage.music


from Elara.console.logging import logger


from Elara.style import color


import traceback, sys


import asyncio


from Elara.engine.Bot import AutoShardedBot


from Elara.workflows.ui import create_music_controller_image


import datetime


import storage


import re


def is_link(text):

    # Define a regex pattern to match URLs

    pattern = re.compile(
        r"^(https?:\/\/)?"  # Match the protocol (http or https)
        r"((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|"  # Match domain (e.g. example.com)
        r"((\d{1,3}\.){3}\d{1,3}))"  # Match IP address (e.g. 192.168.0.1)
        r"(:\d+)?(\/\S*)?$",  # Optional port and resource path
        re.IGNORECASE,
    )

    return re.match(pattern, text) is not None


def convert_ms_to_beautiful_time(ms: int):

    try:

        seconds = ms // 1000

        minutes, seconds = divmod(seconds, 60)

        hours, minutes = divmod(minutes, 60)

        days, hours = divmod(hours, 24)

        weeks, days = divmod(days, 7)

        months, weeks = divmod(weeks, 4)

        time = ""

        if months:

            time += f"{months}M "

        if weeks:

            time += f"{weeks}W "

        if days:

            time += f"{days}D "

        if hours:

            time += f"{hours}h "

        if minutes:

            time += f"{minutes}m "

        if seconds:

            time += f"{seconds}s"

        return time.strip() or "0s"

    except Exception as e:

        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

        return "Unknown"


class ElaraMusicControllerView(discord.ui.View):
    def __init__(
        self,
        cog: "Music",
        guild: discord.Guild,
        player: wavelink.Player,
        artwork_media: str,
        interactive: bool = True,
    ) -> None:
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
        self.player = player
        self.interactive = interactive
        self.artwork_media = artwork_media
        self._update_buttons()

    def _update_buttons(self):
        if not self.player:
            return

        is_paused = self.player.paused
        self.pause_resume_button.label = "Resume" if is_paused else "Pause"
        self.pause_resume_button.emoji = self.cog.bot.emoji.PLAYING if is_paused else self.cog.bot.emoji.PAUSED
        
        is_loop = self.player.queue.mode == wavelink.QueueMode.loop
        self.loop_button.style = discord.ButtonStyle.primary if is_loop else discord.ButtonStyle.secondary
        
        is_autoplay = self.player.autoplay != wavelink.AutoPlayMode.disabled
        self.autoplay_button.style = discord.ButtonStyle.primary if is_autoplay else discord.ButtonStyle.secondary

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.secondary, row=0)
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.pause_resume_button_callback(interaction)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, row=0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.skip_button_callback(interaction)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.stop_button_callback(interaction)

    @discord.ui.button(label="Loop", emoji="🔁", style=discord.ButtonStyle.secondary, row=1)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.loop_toggle_callback(interaction)

    @discord.ui.button(label="Shuffle", emoji="🔀", style=discord.ButtonStyle.secondary, row=1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.shuffle_button_callback(interaction)

    @discord.ui.button(label="Autoplay", emoji="📻", style=discord.ButtonStyle.secondary, row=1)
    async def autoplay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.autoplay_toggle_callback(interaction)

    @discord.ui.select(
        placeholder="Select Audio Filter...",
        options=[
            discord.SelectOption(label="None", value="none", emoji="❌", description="Remove all filters"),
            discord.SelectOption(label="Bass Boost", value="bassboost", emoji="🔊", description="Heavy bass enhancement"),
            discord.SelectOption(label="Soft Bass", value="softbass", emoji="🔉", description="Light bass enhancement"),
            discord.SelectOption(label="Nightcore", value="nightcore", emoji="⚡", description="High pitch and faster tempo"),
            discord.SelectOption(label="Vaporwave", value="vaporwave", emoji="🌊", description="Slowed and aesthetic"),
            discord.SelectOption(label="Pop", value="pop", emoji="🎤", description="Pop music equalizer"),
            discord.SelectOption(label="Classic", value="classic", emoji="🎻", description="Classical music equalizer")
        ],
        row=2
    )
    async def filter_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await self.cog.select_filter_callback(interaction)


class Music(commands.Cog):

    CONTROLLER_COOLDOWN_SECONDS = 1.5

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Music"

            category = "Main"

            description = "Music commands"

            hidden = False

            emoji = self.bot.emoji.MUSIC 

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

    @commands.hybrid_command(
        name="play",
        aliases=["p"],
        help="Play music in the voice channel.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def play(self, ctx: commands.Context, *, search: str = None):
        if not search:
            embed = discord.Embed(
                description=(
                    f"**Music System** {self.bot.emoji.MUSIC}\n"
                    "Stream high-quality audio directly into your voice channel.\n\n"
                    "**__Usage:__**\n"
                    f"> `{self.bot.BotConfig.PREFIX}play <query>`\n"
                    f"> `{self.bot.BotConfig.PREFIX}play <link>`\n\n"
                    "**__Details:__**\n"
                    "> Supports YouTube, Spotify, Soundcloud & more.\n"
                    "> Use the buttons in the controller to manage the session."
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            return await ctx.reply(embed=embed)

        try:

            if ctx.interaction:

                await ctx.defer()

            music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

            if music_data:

                if music_data.get("music_setup_channel_id", None):

                    # send to use the setuped channel to play music

                    embed = discord.Embed(
                        description=f"Send anything in the channel <#{music_data.get('music_setup_channel_id',None)}> to play music.",
                        color=0x2b2d31,
                    )

                    embed.set_author(
                        name=ctx.guild.name,
                        icon_url=(
                            ctx.guild.icon.url
                            if ctx.guild.icon
                            else self.bot.user.display_avatar.url
                        ),
                        url=self.bot.urls.WEBSITE,
                    )

                    embed.set_footer(
                        text=f"Use /resetmusic to reset the setup of music"
                    )

                    return await ctx.reply(embed=embed)

            # Check if the user is in a voice channel

            if not ctx.author.voice:

                await ctx.reply(
                    "You need to be in a voice channel to use this command."
                )

                return

            try:

                # Check if the user is in a voice channel

                if not ctx.author.voice:

                    return await ctx.reply(
                        f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.",
                        delete_after=10,
                    )

                destination = ctx.author.voice.channel

                # Connect to the voice channel if not already connected

                if not ctx.guild.voice_client:

                    vc: wavelink.Player = await destination.connect(
                        cls=wavelink.Player, timeout=60, self_deaf=True
                    )

                    music_settings = self.bot.cache.music.get(str(ctx.guild.id), {})
                    if not music_settings:
                        music_settings = await storage.music.get(guild_id=ctx.guild.id) or {}
                    vc.inactive_timeout = None if music_settings.get("stay_24_7") else 10

                else:

                    vc: wavelink.Player = ctx.guild.voice_client

                    # if the bot is another vc and not playing anything then move to the new vc

                    if vc.channel.id != destination.id:

                        if not vc.current:

                            await vc.move_to(destination)

                        else:

                            return await ctx.reply(
                                f"{self.bot.emoji.ERROR} | The bot is already playing in another voice channel.",
                                delete_after=10,
                            )

                if ctx.author.voice.channel.id != vc.channel.id:

                    return await ctx.reply(
                        f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.",
                        delete_after=10,
                    )

                users_no_prefix_subscription = self.bot.cache.users.get(
                    str(ctx.author.id), {}
                ).get("no_prefix_subscription", None)

                guilds_subscription = self.bot.cache.guilds.get(
                    str(ctx.guild.id), {}
                ).get("subscription", "free")

                # Use the new search methood correctly

                # Use YouTube Music for better reliability and audio quality
                if is_link(search):
                    result = await wavelink.Playable.search(search)
                else:
                    result = await wavelink.Playable.search(search, source=wavelink.TrackSource.YouTubeMusic)

                if not result:

                    return await ctx.reply(
                        f"{self.bot.emoji.ERROR} | No results found for the search query.",
                        delete_after=10,
                    )

                if isinstance(result, wavelink.Playlist):
                    added_count = 0
                    for t in result.tracks:
                        if len(vc.queue) >= 10:
                            break
                        t.requester = ctx.author
                        if not vc.current:
                            await vc.play(t)
                            await self.send_music_controls(ctx.guild, update_attachments=True, command_channel=ctx.channel)
                        else:
                            await vc.queue.put_wait(t)
                        added_count += 1

                    # Redundant playlist embed removed as requested
                    return

                track = result[0]
                track.requester = ctx.author

                if not vc.current:
                    if guilds_subscription == "free":
                        default_volume = 80
                    else:
                        default_volume = self.bot.cache.music.get(
                            str(ctx.guild.id), {}
                        ).get("default_volume", 80)

                    await vc.play(track, volume=default_volume)

                    await self.send_music_controls(
                        ctx.guild, update_attachments=True, command_channel=ctx.channel
                    )

                else:
                    if len(vc.queue) >= 10:
                        return await ctx.reply(
                            f"{self.bot.emoji.LIMIT} | You can only add up to 10 tracks in the queue.",
                            delete_after=10,
                        )

                    await vc.queue.put_wait(track)
                    await self.send_music_controls(ctx.guild, command_channel=ctx.channel)

                    # Cute compact embed
                    embed = discord.Embed(
                        description=f"**Added to Queue** {self.bot.emoji.MUSIC}\n"
                        f"**[{track.title}]({track.uri})**\n\n"
                        f"**Author:** {track.author}\n"
                        f"**Duration:** `{convert_ms_to_beautiful_time(track.length)}`",
                        color=0x2b2d31
                    )
                    if track.artwork:
                        embed.set_thumbnail(url=track.artwork)
                    embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                    await ctx.send(embed=embed, delete_after=10)


            except TimeoutError:

                return await ctx.reply(
                    embed=discord.Embed(
                        description="The bot took too long to connect to the voice channel.\nPlease try again after changing the voice channel region.",
                        color=0x2b2d31,
                    ),
                    delete_after=10,
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="247",
        aliases=["24/7", "twentyfour-seven"],
        help="Toggle 24/7 mode for the music bot.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.has_permissions(manage_guild=True)
    async def twenty_four_seven(self, ctx: commands.Context):
        music_data = await storage.music.get(guild_id=ctx.guild.id)
        if not music_data:
            await storage.music.insert(guild_id=ctx.guild.id)
            music_data = await storage.music.get(guild_id=ctx.guild.id)
            
        current_state = music_data.get("stay_24_7", False)
        new_state = not current_state
        
        await storage.music.update(id=music_data.get("id"), stay_24_7=new_state)
        
        vc: wavelink.Player = ctx.guild.voice_client
        if vc:
            vc.inactive_timeout = None if new_state else 10
            
        status = self.bot.emoji.ENABLED if new_state else self.bot.emoji.DISABLED
        await self.send_success_embed(ctx, f"24/7 mode is now {status}")

    @commands.hybrid_command(
        name="join",
        aliases=["connect", "j"],
        help="Make the bot join your voice channel.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def join_command(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await self.send_denied_embed(ctx, "You need to be in a voice channel for me to join.")

        destination = ctx.author.voice.channel

        if ctx.guild.voice_client:
            if ctx.guild.voice_client.channel.id == destination.id:
                return await self.send_denied_embed(ctx, "I'm already in your voice channel!")
            
            await ctx.guild.voice_client.move_to(destination)
            return await self.send_success_embed(ctx, f"Moved to {destination.mention}")

        await destination.connect(cls=wavelink.Player, self_deaf=True)
        return await self.send_success_embed(ctx, f"Joined {destination.mention}")

    music_controller_view_timeout_data = {}  # {guild_id: datetime.datetime}

    async def _validate_controller_interaction(self, interaction: discord.Interaction):

        vc: wavelink.Player = interaction.guild.voice_client

        if not vc:

            await interaction.response.send_message(
                embed=discord.Embed(
                    description="The player is offline right now.", color=0x2b2d31
                ),
                ephemeral=True,
                delete_after=8,
            )

            return None

        if not interaction.user.voice:

            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Join a voice channel to use the controller.",
                    color=0x2b2d31,
                ),
                ephemeral=True,
                delete_after=8,
            )

            return None

        if vc.channel != interaction.user.voice.channel:

            await interaction.response.send_message(
                embed=discord.Embed(
                    description="You need to be in the same voice channel as Elara.",
                    color=0x2b2d31,
                ),
                ephemeral=True,
                delete_after=8,
            )

            return None

        last_used = self.music_controller_view_timeout_data.get(interaction.guild.id)

        if last_used and datetime.datetime.now() - last_used < datetime.timedelta(
            seconds=self.CONTROLLER_COOLDOWN_SECONDS
        ):

            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Controller is refreshing, try again in a moment.",
                    color=0x2b2d31,
                ),
                ephemeral=True,
                delete_after=4,
            )

            return None

        self.music_controller_view_timeout_data[interaction.guild.id] = (
            datetime.datetime.now()
        )

        return vc

    async def _send_controller_toast(
        self, interaction: discord.Interaction, message: str
    ):

        try:

            embed = discord.Embed(description=f"{message}", color=0x2b2d31)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{interaction.user.name}", icon_url=self.bot.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    def _truncate_track_text(self, text: str, limit: int) -> str:

        if not text:

            return "Unknown"

        return text if len(text) <= limit else f"{text[:limit - 3]}..."

    def _build_queue_summary(self, player: Union[wavelink.Player, None]) -> str:

        if not player or not player.current:

            return "**Queue**\n-# No active session right now."

        lines = [
            f"**Queue**",
            f"**Now** - `{self._truncate_track_text(player.current.title, 52)}`",
        ]

        queue_items = list(player.queue)

        if queue_items:

            for index, track in enumerate(queue_items[:3], start=1):

                lines.append(
                    f"**Next {index}** - `{self._truncate_track_text(track.title, 44)}` - `{convert_ms_to_beautiful_time(track.length)}`"
                )

            if len(queue_items) > 3:

                lines.append(f"-# +{len(queue_items) - 3} more waiting")

        else:

            lines.append("-# Queue is empty")

        return "\n".join(lines)

    async def _resolve_controller_message(
        self, guild: discord.Guild, command_channel: discord.Union[TextChannel, None]
    ):

        music_data = self.bot.cache.music.get(str(guild.id), {})

        controller_message = self.manual_controller_data.get(str(guild.id))

        target_channel = command_channel

        if music_data.get("music_setup_channel_id"):

            target_channel = guild.get_channel(music_data.get("music_setup_channel_id"))

            if target_channel:
                
                # Check if we already have the message object cached
                if not controller_message or controller_message.id != music_data.get("music_setup_message_id"):

                    try:

                        controller_message = await target_channel.fetch_message(
                            music_data.get("music_setup_message_id")
                        )
                        # Cache it in manual_controller_data even for setup channels to avoid redundant fetches
                        self.manual_controller_data[str(guild.id)] = controller_message

                    except Exception:

                        controller_message = None

        return target_channel, controller_message, music_data

    async def select_filter_callback(self, interaction: discord.Interaction):

        try:

            vc: wavelink.Player = interaction.guild.voice_client

            if not vc:

                return await interaction.response.send_message(
                    embed=discord.Embed(
                        description="The bot is not connected to any voice channel.",
                        color=0x2b2d31,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

            if not interaction.user.voice:

                return await interaction.response.send_message(
                    embed=discord.Embed(
                        description="You need to be in a voice channel to use this button.",
                        color=0x2b2d31,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

            if vc.channel != interaction.user.voice.channel:

                return await interaction.response.send_message(
                    embed=discord.Embed(
                        description="You need to be in the same voice channel as the bot to use this button.",
                        color=0x2b2d31,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

            # Rate limiting

            if self.music_controller_view_timeout_data.get(
                interaction.guild.id, None
            ) and datetime.datetime.now() - self.music_controller_view_timeout_data[
                interaction.guild.id
            ] < datetime.timedelta(
                seconds=10
            ):

                return await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.TIME} | Clicking too fast.",
                        color=0x2b2d31,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

            self.music_controller_view_timeout_data[interaction.guild.id] = (
                datetime.datetime.now()
            )

            await interaction.response.defer()

            # Get the selected filter
            selected_filter = interaction.data["values"][0]

            filters = wavelink.Filters()

            if selected_filter == "none":
                await vc.set_filters(None, seek=True)
                await self.send_music_controls(interaction.guild, update_attachments=True)
                return await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Filter has been removed.", ephemeral=True)

            elif selected_filter == "bassboost":
                # Strong bass boost using equalizer
                filters.equalizer.set(bands=[{"band": 0, "gain": 0.6}, {"band": 1, "gain": 0.45}, {"band": 2, "gain": 0.3}, {"band": 3, "gain": 0.15}])
                
            elif selected_filter == "softbass":
                filters.equalizer.set(bands=[{"band": 0, "gain": 0.25}, {"band": 1, "gain": 0.15}, {"band": 2, "gain": 0.05}])

            elif selected_filter == "nightcore":
                filters.timescale.set(speed=1.2, pitch=1.2, rate=1.0)

            elif selected_filter == "vaporwave":
                filters.timescale.set(speed=0.85, pitch=0.8, rate=1.0)

            elif selected_filter == "pop":
                filters.equalizer.set(bands=[{"band": 0, "gain": -0.1}, {"band": 1, "gain": 0.1}, {"band": 2, "gain": 0.2}, {"band": 3, "gain": 0.3}, {"band": 4, "gain": 0.2}, {"band": 5, "gain": 0.1}, {"band": 6, "gain": -0.1}])

            elif selected_filter == "classic":
                filters.equalizer.set(bands=[{"band": 0, "gain": 0.3}, {"band": 1, "gain": 0.2}, {"band": 2, "gain": 0.1}, {"band": 3, "gain": 0.0}, {"band": 4, "gain": 0.0}, {"band": 5, "gain": 0.1}, {"band": 6, "gain": 0.2}])

            elif selected_filter == "hq":
                # Crystal Clear HQ: Subtle bass boost + enhanced treble for clarity
                filters.equalizer.set(bands=[
                    {"band": 0, "gain": 0.15}, {"band": 1, "gain": 0.1}, # Low
                    {"band": 2, "gain": 0.05}, {"band": 3, "gain": 0.0}, # Mid
                    {"band": 4, "gain": 0.05}, {"band": 5, "gain": 0.1}, # High-Mid
                    {"band": 6, "gain": 0.2}, {"band": 7, "gain": 0.25}  # Treble/Air
                ])

            await vc.set_filters(filters, seek=True)
            await self.send_music_controls(interaction.guild, update_attachments=True)
            
            embed = discord.Embed(
                title=f"{self.bot.emoji.SUCCESS} Filter Set",
                description=f"» Audio filter has been set to **{selected_filter.title()}**.",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Action by {interaction.user.name} ({interaction.user.id})")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def volume_down_button_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            if vc.volume <= 0:
                embed = discord.Embed(
                    title=f"{self.bot.emoji.ERROR} Volume Error",
                    description="» Volume is already at **minimum** (0%).", 
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Action by {interaction.user.name} ({interaction.user.id})")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            new_volume = max(0, vc.volume - 10)
            await vc.set_volume(new_volume)

            await self.send_music_controls(interaction.guild, update_attachments=True)

            embed = discord.Embed(
                title=f"{self.bot.emoji.SUCCESS} Volume Set",
                description=f"» Player volume is set to **{new_volume}/200** now.",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Action by {interaction.user.name} ({interaction.user.id})")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def stop_button_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            await interaction.response.defer()

            vc.queue.clear()

            await vc.stop()

            await vc.disconnect()

            await self.send_music_controls(interaction.guild, end=True)

            await self._send_controller_toast(interaction, "Player stopped.")

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def shuffle_button_callback(self, interaction: discord.Interaction):
        try:
            vc = await self._validate_controller_interaction(interaction)
            if not vc: return
            
            if len(vc.queue) < 2:
                embed = discord.Embed(
                    title="Process Denied !",
                    description=f"{self.bot.emoji.ERROR} Not enough tracks in queue to shuffle!",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{interaction.user.name}", icon_url=self.bot.user.display_avatar.url)
                return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            
            await interaction.response.defer()
            vc.queue.shuffle()
            await self.send_music_controls(interaction.guild)
            await self._send_controller_toast(interaction, "Queue shuffled!")
        except Exception as e:
            logger.error(f"Error in shuffle_button_callback: {e}")

    async def pause_resume_button_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            await interaction.response.defer()

            if vc.paused:

                await vc.pause(False)

                await self.send_music_controls(
                    interaction.guild, update_attachments=True
                )

                await self._send_controller_toast(interaction, "Playback resumed.")

            else:

                await vc.pause(True)

                await self.send_music_controls(
                    interaction.guild, update_attachments=True
                )

                await self._send_controller_toast(interaction, "Playback paused.")

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def skip_button_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            await interaction.response.defer()

            if vc.queue or vc.autoplay != wavelink.AutoPlayMode.disabled:

                await vc.skip(force=True)

                await self._send_controller_toast(interaction, "Skipped current track.")

            else:

                await self._send_controller_toast(
                    interaction, "Nothing left in queue to skip into."
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def volume_up_button_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            if vc.volume >= 200:
                embed = discord.Embed(
                    title=f"{self.bot.emoji.ERROR} Volume Error",
                    description="» Volume is already at **maximum** (200%).", 
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Action by {interaction.user.name} ({interaction.user.id})")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            new_volume = min(200, vc.volume + 10)
            await vc.set_volume(new_volume)
            await self.send_music_controls(interaction.guild, update_attachments=True)

            embed = discord.Embed(
                title=f"{self.bot.emoji.SUCCESS} Volume Set",
                description=f"» Player volume is set to **{new_volume}/200** now.",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Action by {interaction.user.name} ({interaction.user.id})")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def loop_toggle_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            await interaction.response.defer()

            if vc.queue.mode == wavelink.QueueMode.loop:

                vc.queue.mode = wavelink.QueueMode.normal

                await self.send_music_controls(
                    interaction.guild, update_attachments=True
                )

                await self._send_controller_toast(interaction, "Loop disabled.")

            else:

                vc.queue.mode = wavelink.QueueMode.loop

                await self.send_music_controls(
                    interaction.guild, update_attachments=True
                )

                await self._send_controller_toast(interaction, "Loop enabled.")

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def autoplay_toggle_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            await interaction.response.defer()

            if vc.autoplay == wavelink.AutoPlayMode.disabled:

                vc.autoplay = wavelink.AutoPlayMode.enabled

                await self.send_music_controls(
                    interaction.guild, update_attachments=True
                )

                await self._send_controller_toast(interaction, "Autoplay enabled.")

            else:

                vc.autoplay = wavelink.AutoPlayMode.disabled

                await self.send_music_controls(
                    interaction.guild, update_attachments=True
                )

                await self._send_controller_toast(interaction, "Autoplay disabled.")

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def set_volume_button_callback(self, interaction: discord.Interaction):

        try:

            vc = await self._validate_controller_interaction(interaction)

            if not vc:

                return

            class set_volume_modal(discord.ui.Modal, title="Set Volume"):

                new_volume_field = discord.ui.TextInput(
                    label="Volume",
                    min_length=1,
                    max_length=3,
                    required=True,
                    default=str(vc.volume),
                    placeholder="Volume (0-100)",
                    style=discord.TextStyle.short,
                )

                bot = self.bot

                send_music_controls = self.send_music_controls

                async def on_submit(self, interaction: discord.Interaction):

                    try:

                        vc: wavelink.Player = interaction.guild.voice_client

                        if not vc:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="The bot is not connected to any voice channel.",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        if not interaction.user.voice:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You need to be in a voice channel to use this button.",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        if vc.channel != interaction.user.voice.channel:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You need to be in the same voice channel as the bot to use this button.",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        try:

                            volume = int(self.new_volume_field.value)

                        except Exception:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="Invalid volume value.", color=0x2b2d31
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        if not 0 <= volume <= 100:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="Volume must be between 0 and 100.",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.defer()

                        await vc.set_volume(volume)

                        await self.send_music_controls(
                            interaction.guild, update_attachments=True
                        )

                        await interaction.followup.send(
                            f"Volume set to `{volume}%`.", ephemeral=True
                        )

                    except Exception:

                        logger.error(
                            f"Error in file {__file__}: {traceback.format_exc()}"
                        )

            await interaction.response.send_modal(set_volume_modal())

        except Exception:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    manual_controller_data = (
        {}
    )  # {guild_id: discord.Message}  # Store the controller message for each guild

    async def send_music_controls(
        self,
        guild: discord.Guild,
        update_attachments: bool = False,
        end: bool = False,
        command_channel: discord.TextChannel = None,
    ):

        try:

            target_channel, controller_message, music_data = (
                await self._resolve_controller_message(guild, command_channel)
            )

            vc: Union[wavelink.Player, None] = guild.voice_client

            if end or not vc or not vc.current:

                idle_view = ElaraMusicControllerView(
                    cog=self,
                    guild=guild,
                    player=None,
                    artwork_media=self.bot.urls.DEFAULT_MUSIC_BANNER,
                    interactive=False,
                )

                if controller_message:
                    try:
                        await controller_message.edit(view=idle_view, attachments=[])
                    except discord.NotFound:
                        controller_message = None
                    except Exception as e:
                        logger.error(f"Error editing idle controller: {e}")
                        controller_message = None

                if not controller_message and target_channel:
                    try:
                        controller_message = await target_channel.send(view=idle_view)
                    except Exception as e:
                        logger.error(f"Error sending idle controller: {e}")


                if music_data.get("music_setup_channel_id") and controller_message:

                    await storage.music.update(
                        id=music_data.get("id"),
                        music_setup_message_id=controller_message.id,
                    )

                elif str(guild.id) in self.manual_controller_data:

                    del self.manual_controller_data[str(guild.id)]

                return

            should_render_image = update_attachments or controller_message is None

            file = None
            music_controller_image = None

            artwork_media = vc.current.artwork or self.bot.urls.DEFAULT_MUSIC_BANNER

            if should_render_image:

                try:

                    music_controller_image = create_music_controller_image(
                        music_thumbnail_url=artwork_media,
                        music_title=vc.current.title,
                        music_author=vc.current.author,
                        music_album=getattr(
                            getattr(vc.current, "album", None), "name", "Single"
                        ),
                        music_duration=vc.current.length,
                        current_position=max(0, getattr(vc, "position", 0)),
                        volume=vc.volume,
                        queue_size=len(vc.queue),
                        is_paused=vc.paused,
                        autoplay_enabled=vc.autoplay != wavelink.AutoPlayMode.disabled,
                        loop_enabled=vc.queue.mode == wavelink.QueueMode.loop,
                    )

                    if music_controller_image:

                        file = discord.File(
                            music_controller_image, filename="music_controller.png"
                        )

                        artwork_media = "attachment://music_controller.png"

                except Exception:

                    logger.error(f"Traceback: {traceback.format_exc()}")

            # Build standard premium embed for controller
            current = vc.current
            requester = getattr(current, "requester", None)
            pos = convert_ms_to_beautiful_time(max(getattr(vc, 'position', 0), 0))
            dur = convert_ms_to_beautiful_time(current.length)
            
            embed = discord.Embed(
                description=f"**Now Playing** {self.bot.emoji.MUSIC}\n"
                f"**[{current.title}]({current.uri})**\n\n"
                f"**Author:** {current.author}\n"
                f"**Requester:** {requester.mention if requester else 'Auto-Played'}\n"
                f"**Queue:** `{len(vc.queue)} tracks`",
                color=0x2b2d31
            )
            if file:
                embed.set_image(url="attachment://music_controller.png")
            elif current.artwork:
                embed.set_image(url=current.artwork)
                
            embed.set_footer(text=f"Toxic (7ox4) • Action by @7ox4", icon_url=self.bot.user.display_avatar.url)

            view = ElaraMusicControllerView(
                cog=self,
                guild=guild,
                player=vc,
                artwork_media=artwork_media,
                interactive=True,
            )

            if not target_channel:

                target_channel = command_channel

            if not target_channel and controller_message:

                target_channel = controller_message.channel

            if not target_channel:

                logger.warning(f"Music controller channel missing for {guild.name}")

                return

            if not controller_message:
                try:
                    controller_message = await target_channel.send(
                        embed=embed,
                        view=view,
                        file=file if file else None,
                    )
                except Exception as e:
                    logger.error(f"Error sending controller: {e}")
            else:
                edit_kwargs = {"embed": embed, "view": view}
                if file:
                    edit_kwargs["attachments"] = [file]
                try:
                    await controller_message.edit(**edit_kwargs)
                except discord.NotFound:
                    # Re-send if message was deleted
                    try:
                        if music_controller_image:
                            music_controller_image.seek(0)
                            file = discord.File(music_controller_image, filename="music_controller.png")
                        controller_message = await target_channel.send(embed=embed, view=view, file=file)
                    except Exception as e:
                        logger.error(f"Error re-sending controller: {e}")
                except Exception as e:
                    logger.error(f"Error editing controller: {e}")


            if music_data.get("music_setup_channel_id"):

                await storage.music.update(
                    id=music_data.get("id"),
                    music_setup_message_id=controller_message.id,
                )

            else:

                self.manual_controller_data[str(guild.id)] = controller_message

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


    @commands.hybrid_command(
        name="pause", help="Pause the player.", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def pause(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client

        if vc:

            if ctx.interaction:

                await ctx.defer()

            if not ctx.author.voice:

                return await ctx.send(
                    f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.",
                    delete_after=10,
                )

            if vc.channel != ctx.author.voice.channel:

                return await ctx.send(
                    f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.",
                    delete_after=10,
                )

            if vc.paused:
                embed = discord.Embed(
                    description=f"{self.bot.emoji.ERROR} The player is already paused",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                return await ctx.send(embed=embed)

            await vc.pause(True)
            await self.send_music_controls(ctx.guild)
            
            embed = discord.Embed(
                description=f"{self.bot.emoji.SUCCESS} Paused the player",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(
                description=f"{self.bot.emoji.ERROR} No music is currently playing to pause",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed, delete_after=10)

    @commands.hybrid_command(
        name="resume", help="Resume the player.", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def resume(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client

        if vc:
            if ctx.interaction:
                await ctx.defer()

            if not ctx.author.voice:
                embed = discord.Embed(
                    description=f"{self.bot.emoji.ERROR} You need to be in a voice channel",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                return await ctx.send(embed=embed, delete_after=10)

            if vc.channel != ctx.author.voice.channel:
                embed = discord.Embed(
                    title="Process Denied !",
                    description=f"{self.bot.emoji.ERROR} You need to be in the same voice channel as the bot to use this command.",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                return await ctx.send(embed=embed, delete_after=10)

            if not vc.paused:
                embed = discord.Embed(
                    title="Process Denied !",
                    description=f"{self.bot.emoji.ERROR} No music is currently paused to resume.",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                return await ctx.send(embed=embed)

            await vc.pause(False)
            await self.send_music_controls(ctx.guild)

            await ctx.reply(f"{self.bot.emoji.PLAYING} | Resumed the player.")

        else:

            await ctx.send(
                f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.",
                delete_after=10,
            )

    @commands.command(name="skip")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def skip(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client

        # Check if the user is in a voice channel

        if not ctx.author.voice:

            return await ctx.send(
                f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.",
                delete_after=10,
            )

        # Check if the bot is in a voice channel

        if not vc:

            return await ctx.send(
                f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.",
                delete_after=10,
            )

        # Check if the bot and user are in the same voice channel

        if vc and vc.channel != ctx.author.voice.channel:

            return await ctx.send(
                f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.",
                delete_after=10,
            )

        if ctx.interaction:

            await ctx.defer()

        # Check if there is a track currently playing or paused

        if vc.playing or vc.paused:
            await vc.stop()
            embed = discord.Embed(
                description=f"{self.bot.emoji.SUCCESS} Skipped the current track",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(
                description=f"{self.bot.emoji.ERROR} No track is currently playing or paused",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed, delete_after=10)

    @commands.hybrid_command(
        name="loop", help="Loop the current track.", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def loop(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client

        if not vc:
            return await self.send_denied_embed(ctx, "The bot is not connected to any voice channel.")

        # Check if the user is in a voice channel
        if not ctx.author.voice:
            return await self.send_denied_embed(ctx, "You need to be in a voice channel to use this command.")

        # Check if the bot and user are in the same voice channel

        if vc.channel != ctx.author.voice.channel:
            return await self.send_denied_embed(ctx, "You need to be in the same voice channel as the bot to use this command.")

        if ctx.interaction:

            await ctx.defer()

        # Toggle loop mode between 'normal' and 'loop'

        if vc.queue.mode == wavelink.QueueMode.loop:
            vc.queue.mode = wavelink.QueueMode.normal
            await self.send_success_embed(ctx, "Looping has been disabled.")

        else:
            vc.queue.mode = wavelink.QueueMode.loop
            await self.send_success_embed(ctx, "Looping has been enabled.")

    @commands.hybrid_command(
        name="queue",
        aliases=["q", "tracks", "track"],
        help="Show the queue of the player.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def queue(self, ctx: commands.Context):

        try:

            vc: wavelink.Player = ctx.guild.voice_client

            if vc:

                if ctx.interaction:

                    await ctx.defer()

                async def get_embed():

                    embed = discord.Embed(
                        title="Track Queue", description="", color=0x2b2d31
                    )

                    if vc.current:

                        cuted_title = (
                            vc.current.title[:50] + "..."
                            if len(vc.current.title) > 50
                            else vc.current.title
                        )

                        embed.description += f"**{self.bot.emoji.PAUSED if vc.paused else self.bot.emoji.PLAYING} 1. [{cuted_title}]({self.bot.urls.SUPPORT_SERVER}) - `{convert_ms_to_beautiful_time(vc.current.length)}`**\n"

                    for index, track in enumerate(vc.queue, start=2):

                        cuted_title = (
                            track.title[:50] + "..."
                            if len(track.title) > 50
                            else track.title
                        )

                        embed.description += f"**{self.bot.emoji.QUEUE} {index}. [{cuted_title}]({self.bot.urls.SUPPORT_SERVER}) - `{convert_ms_to_beautiful_time(track.length)}`**\n"

                    return embed

                timeout_time = 60

                cancled = False

                def reset_timeout_time():

                    nonlocal timeout_time

                    timeout_time = 60

                async def get_view(disabled=False):

                    view = discord.ui.View()

                    reset_timeout_time()

                    options = []

                    for index, queue in enumerate(vc.queue):

                        try:

                            cuted_title = (
                                queue.title[:50] + "..."
                                if len(queue.title) > 50
                                else queue.title
                            )

                            options.append(
                                discord.SelectOption(
                                    label=cuted_title,
                                    value=str(index),
                                    emoji=self.bot.emoji.QUEUE,
                                    description=f"Length: {convert_ms_to_beautiful_time(queue.length)}",
                                )
                            )

                        except Exception as e:

                            logger.error(f"Error in file {__file__}: {e}")

                    select_to_delete_queue = discord.ui.Select(
                        placeholder="Select a Queue to Delete",
                        options=options,
                        disabled=len(options) == 0,
                    )

                    select_to_delete_queue.callback = (
                        lambda i: select_to_delete_queue_callback(i)
                    )

                    if len(options) != 0:

                        view.add_item(select_to_delete_queue)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                async def select_to_delete_queue_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You can't use this button.",
                                    color=0x2b2d31,
                                ),
                                ephemeral=True,
                                delete_after=5,
                            )

                        await interaction.response.defer()

                        print(interaction.data)

                        track_index = int(interaction.data["values"][0])

                        if track_index == None:

                            return await interaction.edit_original_response(
                                embed=discord.Embed(
                                    description="Invalid track selected.",
                                    color=0x2b2d31,
                                )
                            )

                        if not vc.queue:

                            return await interaction.edit_original_response(
                                embed=discord.Embed(
                                    description="The queue is empty.", color=0x2b2d31
                                )
                            )

                        if len(vc.queue) < track_index - 1:

                            return await interaction.edit_original_response(
                                embed=discord.Embed(
                                    description="Invalid track selected.",
                                    color=0x2b2d31,
                                )
                            )

                        vc.queue.delete(track_index)

                        await interaction.message.edit(
                            embed=await get_embed(), view=await get_view()
                        )

                    except Exception as e:

                        logger.error(f"Error in file {__file__}: {e}")

                message = await ctx.send(embed=await get_embed(), view=await get_view())

                while not cancled:

                    try:

                        timeout_time -= 1

                        if timeout_time <= 0:
                            try:
                                await message.edit(view=await get_view(disabled=True))
                            except:
                                pass
                            break


                        await asyncio.sleep(1)

                    except Exception as e:

                        logger.error(f"Error in file {__file__}: {e}")

            else:

                await ctx.send(
                    f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.",
                    delete_after=10,
                )

        except Exception as e:

            logger.error(f"Traceback: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="volume",
        aliases=["vol", "v"],
        help="Get or set the volume of the player.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def volume(self, ctx: commands.Context, volume: int = None):

        vc: wavelink.Player = ctx.guild.voice_client

        if vc:
            if ctx.interaction:
                await ctx.defer()

            if not ctx.author.voice:
                return await self.send_denied_embed(ctx, "You need to be in a voice channel to use this command.")

            if vc.channel != ctx.author.voice.channel:
                return await self.send_denied_embed(ctx, "You need to be in the same voice channel as the bot to use this command.")

            if not volume:
                await self.send_success_embed(ctx, f"Current volume: `{vc.volume}%`")

            else:
                if volume < 0 or volume > 100:
                    return await self.send_denied_embed(ctx, "Volume must be between 0 and 100.")

                await vc.set_volume(volume)
                filled_blocks = volume // 10
                empty_blocks = 10 - filled_blocks
                text = "█" * filled_blocks + "░" * empty_blocks
                await self.send_success_embed(ctx, f"Volume set to `{volume}%`\n`{text}`")
                await self.send_music_controls(ctx.guild, update_attachments=True)

        else:
            await self.send_denied_embed(ctx, "The bot is not connected to any voice channel.")

            await ctx.send(
                f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.",
                delete_after=10,
            )

    @commands.hybrid_command(
        name="stop",
        aliases=["dc", "leave", "disconnect"],
        help="Stop the player and disconnect the bot from the voice channel.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def stop(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client
        manually_disconnected = False

        if ctx.interaction:
            await ctx.defer()

        if not vc:
            try:
                if ctx.guild.me.voice:
                    await ctx.guild.me.move_to(None)
                    manually_disconnected = True
            except Exception as e:
                logger.error(f"Error in file {__file__}: {e}")

        if vc:
            if not ctx.author.voice:
                return await self.send_denied_embed(ctx, "You need to be in a voice channel to use this command.")

            if vc.channel != ctx.author.voice.channel:
                return await self.send_denied_embed(ctx, "You need to be in the same voice channel as the bot to use this command.")

            vc.queue.clear()
            await vc.stop()
            
            embed = discord.Embed(
                title="🚫 Disconnected",
                description="Successfully stopped the player and left the voice channel.\n\n> Hope you enjoyed the music!\n> See you soon! ✨",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            try:
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in file {__file__}: {e}")

            await vc.disconnect()
            await self.send_music_controls(ctx.guild, end=True)

        elif manually_disconnected:
            embed = discord.Embed(
                description=f"{self.bot.emoji.SUCCESS} The bot has been disconnected from the voice channel ✨",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

        elif not vc and not manually_disconnected:
            await self.send_denied_embed(ctx, "The bot is not connected to any voice channel.")

    @commands.hybrid_command(
        name="current",
        aliases=["nowplaying", "np"],
        help="Show the current playing track.",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def current(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client

        if vc:
            if ctx.interaction:
                await ctx.defer()

            if not vc.current:
                return await self.send_denied_embed(ctx, "No track is currently playing.")

            current = vc.current
            requester = getattr(current, "requester", None)
            
            embed = discord.Embed(
                title="🎶 Now Playing",
                description=f"**[{current.title}]({current.uri})**\n\n> Requested by: {requester.mention if requester else 'Auto-Played'}\n> Duration: `{convert_ms_to_beautiful_time(current.length)}`",
                color=0x2b2d31
            )
            if current.artwork:
                embed.set_thumbnail(url=current.artwork)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed)

        else:
            await self.send_denied_embed(ctx, "The bot is not connected to any voice channel.")

    @commands.hybrid_command(
        name="autoplay", help="Toggle autoplay mode.", with_app_command=True, aliases=["ap"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def autoplay(self, ctx: commands.Context):

        vc: wavelink.Player = ctx.guild.voice_client

        if vc:
            if ctx.interaction:
                await ctx.defer()

            if not ctx.author.voice:
                return await self.send_denied_embed(ctx, "You must be in a voice channel to toggle autoplay.")

            if vc.channel != ctx.author.voice.channel:
                return await self.send_denied_embed(ctx, "You must be in the same voice channel as the bot.")

            if vc.autoplay == wavelink.AutoPlayMode.disabled:
                vc.autoplay = wavelink.AutoPlayMode.enabled
                await self.send_success_embed(ctx, "Autoplay has been enabled. Related tracks will play when the queue ends.")
            else:
                vc.autoplay = wavelink.AutoPlayMode.disabled
                await self.send_success_embed(ctx, "Autoplay has been disabled.")

            await self.send_music_controls(ctx.guild)

        else:
            await self.send_denied_embed(ctx, "The bot is not connected to any voice channel.")

    async def music_setup_function(self, message: discord.Message):

        try:

            # this cuntion will work like play command

            try:

                await message.delete()

            except:

                logger.warning(
                    f"Failed to delete the message in {message.guild.name} for music function"
                )

            if not message.author.voice:

                return await message.channel.send(
                    f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.",
                    delete_after=10,
                )

                # destination = ctx.author.voice.channel

                # # Connect to the voice channel if not already connected

                # if not ctx.guild.voice_client:

                #     vc: wavelink.Player = await destination.connect(cls=wavelink.Player,timeout=60)

                #     vc.inactive_timeout = 10

                # else:

                #     vc: wavelink.Player = ctx.guild.voice_client

                #     # if the bot is another vc and not playing anything then move to the new vc

                #     if vc.channel.id != destination.id:

                #         if not vc.current:

                #             await vc.move_to(destination)

                #         else:

                #             return await ctx.reply(f"{self.bot.emoji.ERROR} | The bot is already playing in another voice channel.",delete_after=10)

            if not message.guild.voice_client:

                vc: wavelink.Player = await message.author.voice.channel.connect(
                    cls=wavelink.Player, timeout=60, self_deaf=True
                )

                music_settings = self.bot.cache.music.get(str(message.guild.id), {})
                if not music_settings:
                    music_settings = await storage.music.get(guild_id=message.guild.id) or {}
                vc.inactive_timeout = None if music_settings.get("stay_24_7") else 10

            else:

                vc: wavelink.Player = message.guild.voice_client

                if vc.channel != message.author.voice.channel:

                    if not vc.current:

                        await vc.move_to(message.author.voice.channel)

                    else:

                        return await message.channel.send(
                            f"{self.bot.emoji.ERROR} | The bot is already playing in another voice channel.",
                            delete_after=5,
                        )

            if not vc.connected:

                return await message.channel.send(
                    f"{self.bot.emoji.ERROR} | Failed to connect to the voice channel.",
                    delete_after=5,
                )

            search = message.content

            if not search:

                return await message.channel.send(
                    f"{self.bot.emoji.ERROR} | Please provide a search query.",
                    delete_after=5,
                )

            users_no_prefix_subscription = self.bot.cache.users.get(
                str(message.author.id), {}
            ).get("no_prefix_subscription", None)

            guilds_subscription = self.bot.cache.guilds.get(
                str(message.guild.id), {}
            ).get("subscription", "free")

            if not users_no_prefix_subscription and guilds_subscription == "free":

                if is_link(search):

                    return await message.channel.send(
                        embed=discord.Embed(
                            description="You can't play music using links in the free subscription.",
                            color=0x2b2d31,
                        ),
                        view=discord.ui.View().add_item(
                            discord.ui.Button(
                                label="Upgrade Subscription",
                                style=discord.ButtonStyle.url,
                                url=self.bot.urls.SUPPORT_SERVER,
                                emoji=self.bot.emoji.SUPPORT,
                            )
                        ),
                    )

            result = await wavelink.Playable.search(
                search, source=wavelink.TrackSource.YouTube
            )

            if not result:

                await vc.disconnect()

                return await message.channel.send(
                    f"{self.bot.emoji.ERROR} | No tracks found.", delete_after=5
                )

            if isinstance(result, wavelink.Playlist):
                added_count = 0
                for t in result.tracks:
                    if len(vc.queue) >= 10:
                        break
                    t.requester = message.author
                    if not vc.current:
                        await vc.play(t)
                        await self.send_music_controls(message.guild, update_attachments=True)
                    else:
                        await vc.queue.put_wait(t)
                        await self.send_music_controls(message.guild, update_attachments=True)
                    added_count += 1

                return

            track = result[0]
            track.requester = message.author

            if not vc.current:
                if guilds_subscription == "free":
                    default_volume = 80
                else:
                    default_volume = self.bot.cache.music.get(
                        str(message.guild.id), {}
                    ).get("default_volume", 80)

                await vc.play(track, volume=default_volume)
                await self.send_music_controls(message.guild, update_attachments=True)

            else:
                if len(vc.queue) >= 10:
                    return await message.channel.send(
                        f"{self.bot.emoji.ERROR} | The queue is full.", delete_after=5
                    )

                await vc.queue.put_wait(track)
                await self.send_music_controls(message.guild)


        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_group(
        name="music",
        help="Music Related Functions",
        invoke_without_command=True,
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def music_group(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="Music Config Commands",
                description=f"Here are the list of commands\n\n",
                color=0x2b2d31,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}**\n"

            else:

                embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name}` - {ctx.command.help}**\n"

            embed.set_footer(
                text=f"Toxic (7ox4)",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @music_group.command(
        name="setup", help="Setup the music channel", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def music_setup(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if ctx.interaction:

                await ctx.defer(ephemeral=True)

            music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

            if not music_data:

                await storage.music.insert(guild_id=ctx.guild.id)

                music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

            if music_data.get("music_setup_channel_id", None):

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | The music channel is already Exists in <#{music_data.get('music_setup_channel_id')}>",
                        color=0x2b2d31,
                    ).set_footer(
                        text=f"Use /music reset to reset the music channel.",
                        icon_url=self.bot.user.display_avatar.url,
                    ),
                    delete_after=10,
                )

            waiting_message = await ctx.send(
                f"{self.bot.emoji.LOADING} | Creating the music channel..."
            )

            try:

                music_setup_channel = await ctx.guild.create_text_channel(
                    name="🎸-music-channel"
                )

            except:

                logger.error(f"Traceback: {traceback.format_exc()}")

                if not ctx.interaction:

                    return await waiting_message.edit(
                        content=f"{self.bot.emoji.ERROR} | Failed to create the music channel.",
                        delete_after=10,
                    )

                else:

                    return await ctx.send(
                        f"{self.bot.emoji.ERROR} | Failed to create the music channel."
                    )

            await storage.music.update(
                id=music_data.get("id"), music_setup_channel_id=music_setup_channel.id
            )

            await waiting_message.edit(
                content=f"{self.bot.emoji.SUCCESS} | Music channel has been created in <#{music_setup_channel.id}>"
            )

            await self.send_music_controls(ctx.guild, end=True)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @music_group.command(
        name="reset", help="Reset the music channel", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def music_reset(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if ctx.interaction:

                await ctx.defer(ephemeral=True)

            music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

            if not music_data:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | The music channel is not exists.",
                        color=0x2b2d31,
                    ).set_footer(
                        text=f"Use /music setup to setup the music channel.",
                        icon_url=self.bot.user.display_avatar.url,
                    ),
                    delete_after=10,
                )

            if not music_data.get("music_setup_channel_id", None):

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | The music channel is not exists.",
                        color=0x2b2d31,
                    ).set_footer(
                        text=f"Use /music setup to setup the music channel.",
                        icon_url=self.bot.user.display_avatar.url,
                    ),
                    delete_after=10,
                )

            waiting_message = await ctx.send(
                f"{self.bot.emoji.LOADING} | Deleting the music channel..."
            )

            try:

                music_setup_channel = ctx.guild.get_channel(
                    music_data.get("music_setup_channel_id")
                )

                if music_setup_channel:

                    await music_setup_channel.delete()

            except:

                logger.error(f"Traceback: {traceback.format_exc()}")

                if not ctx.interaction:

                    return await waiting_message.edit(
                        content=f"{self.bot.emoji.ERROR} | Failed to delete the music channel.",
                        delete_after=10,
                    )

                else:

                    return await ctx.send(
                        f"{self.bot.emoji.ERROR} | Failed to delete the music channel."
                    )

            await storage.music.update(
                id=music_data.get("id"), music_setup_channel_id=""
            )

            await waiting_message.edit(
                content=f"{self.bot.emoji.SUCCESS} | Music channel has been deleted."
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @music_group.command(
        name="settings",
        help="Show the music settings",
        with_app_command=True,
        aliases=["config", "setting"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=4, per=60, type=commands.BucketType.guild)
    async def music_settings(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if ctx.interaction:

                await ctx.defer(ephemeral=True)

            music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

            if not music_data:

                await storage.music.insert(guild_id=ctx.guild.id)

                music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

            async def get_embed():

                music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

                embed = discord.Embed(
                    title="Music Settings",
                    description="Configure the music settings for your server",
                    color=0x2b2d31,
                )

                embed.add_field(
                    name="Default Volume",
                    value=f"`{music_data.get('default_volume',80) if music_data.get('default_volume') else '80'}`",
                    inline=True,
                )

                embed.add_field(
                    name="Music Channel",
                    value=(
                        f"<#{music_data.get('music_setup_channel_id')}>"
                        if music_data.get("music_setup_channel_id")
                        else "`No music channel set`"
                    ),
                    inline=True,
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon_url=ctx.author.display_avatar.url,
                )

                embed.set_author(
                    name=ctx.guild.name,
                    icon_url=(
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                    url=self.bot.urls.WEBSITE,
                )

                embed.set_thumbnail(
                    url=(
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    )
                )

                return embed

            timeout_time = 200

            cancled = False

            def reset_timeout(timeout: int = 200):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled=False):

                try:

                    reset_timeout()

                    music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

                    view = discord.ui.View(timeout=200)

                    default_volume_button = discord.ui.Button(
                        label="Set Default Volume",
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.MASTER_VOLUME,
                        row=0,
                    )

                    music_channels = []

                    if music_data.get("music_setup_channel_id"):

                        try:

                            music_channel = ctx.guild.get_channel(
                                music_data.get("music_setup_channel_id")
                            )

                            if music_channel:

                                music_channels.append(music_channel)

                        except:

                            logger.error(f"Traceback: {traceback.format_exc()}")

                    music_channel_Select = discord.ui.ChannelSelect(
                        placeholder="Select the music channel",
                        min_values=1,
                        max_values=1,
                        row=1,
                        channel_types=[discord.ChannelType.text],
                        default_values=music_channels if music_channels else None,
                    )

                    cancle_button = discord.ui.Button(
                        label="Cancel",
                        style=discord.ButtonStyle.gray,
                        emoji=self.bot.emoji.CANCLED,
                        row=0,
                    )

                    default_volume_button.callback = (
                        lambda i: default_volume_button_callback(i)
                    )

                    music_channel_Select.callback = (
                        lambda i: music_channel_Select_callback(i)
                    )

                    cancle_button.callback = lambda i: cancle_button_callback(i)

                    view.add_item(default_volume_button)

                    view.add_item(music_channel_Select)

                    view.add_item(cancle_button)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

                    return None

            async def default_volume_button_callback(interaction: discord.Interaction):

                try:

                    if ctx.author.id != interaction.user.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                        )

                    guilds_subscription = self.bot.cache.guilds.get(
                        str(message.guild.id), {}
                    ).get("subscription", "free")

                    if guilds_subscription == "free":

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't change the default volume in free subscription.",
                                color=0x2b2d31,
                            ),
                            view=discord.ui.View().add_item(
                                discord.ui.Button(
                                    label="Buy Subscription",
                                    style=discord.ButtonStyle.link,
                                    url=self.bot.urls.SUPPORT_SERVER,
                                    emoji=self.bot.emoji.SUPPORT,
                                )
                            ),
                            ephemeral=True,
                        )

                    class set_default_volume_modal(
                        discord.ui.Modal, title="Set Default Volume"
                    ):

                        new_volume = discord.ui.TextInput(
                            label="Enter the new volume",
                            placeholder="Enter the new volume",
                            required=True,
                            style=discord.TextStyle.short,
                            row=0,
                            default=str(
                                self.bot.cache.music.get(str(ctx.guild.id), {}).get(
                                    "default_volume", 80
                                )
                                if self.bot.cache.music.get(str(ctx.guild.id), {}).get(
                                    "default_volume"
                                )
                                else "80"
                            ),
                        )

                        bot = self.bot

                        async def on_submit(self, interaction: discord.Interaction):

                            try:

                                if ctx.author.id != interaction.user.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You can't interact with this button",
                                            color=0x2b2d31,
                                        ),
                                        ephemeral=True,
                                    )

                                try:

                                    new_volume = int(self.new_volume.value)

                                except:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="Invalid number",
                                            color=0x2b2d31,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                if new_volume < 0 or new_volume > 200:
                                    embed = discord.Embed(
                                        title=f"{self.bot.emoji.ERROR} Volume Error",
                                        description="» Volume must be between **0** and **200**.", 
                                        color=0x2b2d31
                                    )
                                    embed.set_footer(text=f"Action by {interaction.user.name} ({interaction.user.id})")
                                    return await interaction.response.send_message(embed=embed, ephemeral=True)

                                await interaction.response.defer()

                                music_data = self.bot.cache.music.get(
                                    str(ctx.guild.id), {}
                                )

                                print(f"Updating the default volume to {new_volume}")

                                await storage.music.update(
                                    id=music_data.get("id"),
                                    guild_id=ctx.guild.id,
                                    default_volume=new_volume,
                                )

                                print(f"Updated the default volume to {new_volume}")

                                await interaction.message.edit(
                                    embed=await get_embed(), view=await get_view()
                                )

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                                )

                    await interaction.response.send_modal(set_default_volume_modal())

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def music_channel_Select_callback(interaction: discord.Interaction):

                try:

                    if ctx.author.id != interaction.user.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                        )

                    await interaction.response.defer()

                    music_data = self.bot.cache.music.get(str(ctx.guild.id), {})

                    channel = interaction.data["values"]

                    await storage.music.update(
                        id=music_data.get("id"),
                        guild_id=ctx.guild.id,
                        music_setup_channel_id=channel[0],
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if ctx.author.id != interaction.user.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't interact with this button",
                                color=0x2b2d31,
                            ),
                            ephemeral=True,
                        )

                    await interaction.response.defer()

                    nonlocal cancled

                    cancled = True

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            embed = await get_embed()

            view = await get_view()

            message = await ctx.send(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:
                    try:
                        await message.edit(
                            embed=await get_embed(), view=await get_view(disabled=True)
                        )
                    except:
                        pass
                    break


                await asyncio.sleep(1)

        except Exception as e:
            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

async def setup(bot):
    await bot.add_cog(Music(bot))
