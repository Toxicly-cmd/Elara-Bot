from __future__ import annotations
import datetime
from discord.ext import commands

from Elara.console.logging import logger
import Elara.src.checks.checks as checks
import traceback

class ElaraCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,ctx:commands.Context,error):
        if isinstance(error, (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument, commands.CommandOnCooldown, commands.CheckFailure)):
            # Handling these below but don't log them as "Errors" in console
            pass
        else:
            logger.error(f"Error in file {__file__}: {repr(error)}")
            logger.error(f"Error in {ctx.command}, Command: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {error}")

        if isinstance(error, commands.CommandOnCooldown):
            # if the colldown type is user, then the error.retry_after will be the time left for the user to use the command again
            if error.type == commands.BucketType.user:
                await ctx.reply(f"{self.bot.emoji.WARNING} - You are on cooldown. Please retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.guild):
                await ctx.reply(f"{self.bot.emoji.WARNING} - This server is on cooldown. Please retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.channel):
                await ctx.reply(f"{self.bot.emoji.WARNING} - This channel is on cooldown. Please retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>",delete_after=int(error.retry_after))
            else:
                await ctx.reply(f"{self.bot.emoji.WARNING} - Command is on cooldown. Please retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>",delete_after=int(error.retry_after))
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"{self.bot.emoji.WARNING} - Missing argument: `{error.param.name}`\nUsage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`",delete_after=10)
        if isinstance(error, commands.BadArgument):
            await ctx.reply(f"{self.bot.emoji.WARNING} - Invalid argument provided.\nUsage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`",delete_after=10)
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"{self.bot.emoji.WARNING} - You lack the required permissions: `{', '.join(error.missing_perms)}`",delete_after=10)
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(f"{self.bot.emoji.WARNING} - I lack the required permissions: `{', '.join(error.missing_perms)}`",delete_after=10)
        if isinstance(error, commands.NotOwner):
            await ctx.reply(f"{self.bot.emoji.WARNING} - This command is restricted to the bot owner.",delete_after=10)
        if isinstance(error, commands.CheckFailure):
            # Special handling for custom checks
            if checks.check_ignore_predicate in ctx.command.checks:
                return
            if checks.check_blacklist_predicate in ctx.command.checks:
                return
            
            # Default check failure message
            await ctx.reply(f"{self.bot.emoji.WARNING} - Access denied. You do not meet the requirements for this command.",delete_after=10)

async def setup(bot):
    await bot.add_cog(ElaraCommandError(bot))
