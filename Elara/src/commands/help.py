from __future__ import annotations
import discord
from discord.ext import commands
from discord import ui
import Elara.src.checks.checks as checks
from Elara.style import color
import traceback, sys
from Elara.console.logging import logger
from Elara.engine.Bot import AutoShardedBot

class CogInfo:
    def __init__(self, name, category, description, hidden, emoji):
        self.name = name
        self.category = category
        self.description = description
        self.hidden = hidden
        self.emoji = emoji

class ElaraHelp(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot
        self.cog_info = CogInfo(
            name="Help",
            category="Extra",
            description="Help commands",
            hidden=False,
            emoji=self.bot.emoji.HELP,
        )
        self.all_app_commands = None

    @commands.hybrid_command(
        name="help",
        with_app_command=True,
        help="Show all commands in bot",
        aliases=["h"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=10, per=60, type=commands.BucketType.user)
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        try:
            if ctx.interaction and not ctx.interaction.response.is_done():
                await ctx.defer()
            
            if command_name:
                cmd = self.bot.get_command(command_name)
                if not cmd:
                    return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} Command `{command_name}` not found.", color=0x2b2d31), delete_after=10)
                
                embed = discord.Embed(
                    description=(
                        f"**Command Details** {self.bot.emoji.COMMANDS}\n"
                        f"> **Name:** `{cmd.name}`\n"
                        f"> **Description:** {cmd.help or 'No description provided.'}\n"
                        f"> **Usage:** `{self.bot.BotConfig.PREFIX}{cmd.name} {cmd.signature}`\n"
                        f"> **Aliases:** {', '.join(cmd.aliases) if cmd.aliases else 'None'}"
                    ),
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                return await ctx.send(embed=embed)

            view = HomeView(self.bot, ctx)
            
            embed = discord.Embed(
                description=(
                    f"**Hey {ctx.author.name}**, welcome to **Elara** {self.bot.emoji.BOT}\n"
                    f"I am a versatile Discord bot designed to provide you with the best experience. "
                    f"Use the menu below to explore my diverse categories and commands.\n\n"
                    f"{self.bot.emoji.INFO} **Quick Stats**\n"
                    f"> **Commands:** `{len(self.bot.commands)}` Available\n"
                    f"> **Prefix:** `{self.bot.BotConfig.PREFIX}`\n"
                    f"> **Developer:** `7ox4`\n\n"
                    f"{self.bot.emoji.LINK} **Resources**\n"
                    f"> [Invite]({self.bot.urls.INVITE}) • [Support]({self.bot.urls.SUPPORT}) • [Website]({self.bot.urls.WEBSITE})\n"
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.bot.user.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            view.message = await ctx.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            traceback.print_exc()

class BaseHelpView(ui.View):
    def __init__(self, bot, ctx, reported=False, timeout=120):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.reported = reported
        self.message: discord.Message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"**Process Denied** {self.bot.emoji.ERROR}\nThis menu interaction is restricted to the command author.",
                    color=0x2b2d31,
                ).set_footer(text=f"Toxic (7ox4) • Action by @{self.ctx.author.name}", icon_url=self.bot.user.display_avatar.url),
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass

    def get_cog_mapping(self):
        mapping = {
            "Security": ["Security"],
            "Automod": ["Automod"],
            "Moderation": ["Moderation"],
            "Utility": ["Utils"],
            "Greetings": ["Welcomer"],
            "Music": ["Music"],
            "Fun Commands": ["Fun"],
            "Voice Commands": ["Voice"],
            "Tickets": ["Ticket"],
            "Settings": ["More", "Utils"],
            "Developer": ["Root"]
        }
        return mapping

class HomeView(BaseHelpView):
    def __init__(self, bot, ctx, reported=False):
        super().__init__(bot, ctx, reported)
        self.add_item(CategorySelect(self))
        
        # Buttons with sleek design
        self.add_item(discord.ui.Button(label="Support", url=self.bot.urls.SUPPORT, emoji=self.bot.emoji.SUPPORT, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="Invite", url=self.bot.urls.INVITE, emoji=self.bot.emoji.INVITE, style=discord.ButtonStyle.link))

class CategorySelect(ui.Select):
    def __init__(self, view):
        self.help_view = view
        mapping = view.get_cog_mapping()
        options = []
        
        cat_emojis = {
            "Security": view.bot.emoji.SECURITY,
            "Automod": view.bot.emoji.AUTOMOD,
            "Moderation": view.bot.emoji.MODERATION,
            "Utility": view.bot.emoji.UTILS,
            "Greetings": view.bot.emoji.WELCOME,
            "Music": view.bot.emoji.MUSIC,
            "Fun Commands": view.bot.emoji.FUN,
            "Voice Commands": view.bot.emoji.MICROPHONE,
            "Tickets": view.bot.emoji.TICKET,
            "Settings": view.bot.emoji.SETTINGS,
            "Developer": view.bot.emoji.OWNER
        }

        for cat in mapping.keys():
            options.append(discord.SelectOption(
                label=cat,
                value=cat,
                emoji=cat_emojis.get(cat, view.bot.emoji.CATEGORY)
            ))
            
        super().__init__(placeholder="Select a category to view commands...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cat_name = self.values[0]
        mapping = self.help_view.get_cog_mapping()
        target_cogs = mapping.get(cat_name, [])
        
        all_commands = []
        for cog_name in target_cogs:
            cog = self.help_view.bot.get_cog(cog_name)
            if cog:
                all_commands.extend(cog.get_commands())
        
        unique_cmds = {}
        for cmd in all_commands:
            if not cmd.hidden:
                unique_cmds[cmd.name] = cmd
        
        cmd_list = sorted(unique_cmds.values(), key=lambda x: x.name)
        
        embed = discord.Embed(
            description=f"**{cat_name} Commands** {self.help_view.bot.emoji.CATEGORY}\n" + 
                        " , ".join([f"`{cmd.name}`" for cmd in cmd_list]) if cmd_list else "No commands available.",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.help_view.bot.user.display_avatar.url)
        
        view = CategoryView(self.help_view.bot, self.help_view.ctx, cat_name, cmd_list)
        await interaction.response.edit_message(embed=embed, view=view)

class CategoryView(BaseHelpView):
    def __init__(self, bot, ctx, cat_name, cmd_list):
        super().__init__(bot, ctx)
        self.cat_name = cat_name
        self.add_item(HomeButton())
        
        options = [
            discord.SelectOption(
                label=cmd.name, 
                description=cmd.help[:100] if cmd.help else "No description", 
                value=cmd.name,
                emoji=self.bot.emoji.MESSAGE
            )
            for cmd in cmd_list[:25]
        ]
        if options:
            self.add_item(CommandSelect(options, self))

class CommandSelect(ui.Select):
    def __init__(self, options, view):
        self.help_view = view
        super().__init__(placeholder="View detailed command information...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cmd_name = self.values[0]
        cmd = self.help_view.bot.get_command(cmd_name)
        
        embed = discord.Embed(
            description=(
                f"**{cmd.name.title()} Info** {self.bot.emoji.COMMANDS}\n"
                f"> **Description**: {cmd.help or 'No description provided.'}\n"
                f"> **Usage**: `{self.help_view.bot.BotConfig.PREFIX}{cmd.name} {cmd.signature}`\n"
                f"> **Aliases**: {', '.join(cmd.aliases) if cmd.aliases else 'None'}"
            ),
            color=0x2b2d31
        )
        embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.help_view.bot.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed)

class HomeButton(ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary, emoji="<:Back:1498201855208067074>")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=(
                f"**Hey {self.view.ctx.author.name}**, welcome to **Elara** {self.view.bot.emoji.BOT}\n"
                f"I am a versatile Discord bot designed to provide you with the best experience. "
                f"Use the menu below to explore my diverse categories and commands.\n\n"
                f"{self.view.bot.emoji.INFO} **Quick Stats**\n"
                f"> **Commands:** `{len(self.view.bot.commands)}` Available\n"
                f"> **Prefix:** `{self.view.bot.BotConfig.PREFIX}`\n"
                f"> **Developer:** `7ox4`\n\n"
                f"{self.view.bot.emoji.LINK} **Resources**\n"
                f"> [Invite]({self.view.bot.urls.INVITE}) • [Support]({self.view.bot.urls.SUPPORT}) • [Website]({self.view.bot.urls.WEBSITE})\n"
            ),
            color=0x2b2d31
        )
        embed.set_footer(text=f"Powered By Toxic (7ox4)", icon_url=self.view.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.view.bot.user.display_avatar.url)
        
        view = HomeView(self.view.bot, self.view.ctx)
        await interaction.response.edit_message(embed=embed, view=view)

async def setup(bot: AutoShardedBot):
    await bot.add_cog(ElaraHelp(bot))
