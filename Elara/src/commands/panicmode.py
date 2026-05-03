import discord
from discord.ext import commands
import storage
from Elara.memory.cache import cache
import Elara.src.checks.checks as checks

class PanicMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_success_embed(self, ctx, description):
        embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} {description}", color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.group(name="panicmode", help="Panic mode management", invoke_without_command=True)
    async def panicmode_group(self, ctx):
        await ctx.send_help(ctx.command)

    @panicmode_group.command(name="enable")
    async def panicmode_enable(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Panic_Cache = cache.panicmode.get(str(ctx.guild.id), {})
        if not Panic_Cache:
            await storage.panicmode.insert(guild_id=ctx.guild.id, enabled=True)
        else:
            await storage.panicmode.update(id=Panic_Cache.get("id"), guild_id=ctx.guild.id, enabled=True)
        
        # Lockdown logic: mute everyone or lock channels?
        # Typically panicmode might just be a setting that other events check.
        await self.send_success_embed(ctx, "Panic Mode enabled. High-security protocols active.")

    @panicmode_group.command(name="disable")
    async def panicmode_disable(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Panic_Cache = cache.panicmode.get(str(ctx.guild.id), {})
        if Panic_Cache:
            await storage.panicmode.update(id=Panic_Cache.get("id"), guild_id=ctx.guild.id, enabled=False)
        await self.send_success_embed(ctx, "Panic Mode disabled.")

    @panicmode_group.command(name="set")
    async def panicmode_set(self, ctx, punishment: str):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        if punishment.lower() not in ["kick", "ban", "mute"]:
            return await ctx.send("Invalid punishment. Choose from: kick, ban, mute")
        
        Panic_Cache = cache.panicmode.get(str(ctx.guild.id), {})
        await storage.panicmode.update(id=Panic_Cache.get("id"), guild_id=ctx.guild.id, punishment=punishment.lower())
        await self.send_success_embed(ctx, f"Panic Mode punishment set to `{punishment}`")

    @panicmode_group.command(name="reset")
    async def panicmode_reset(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Panic_Cache = cache.panicmode.get(str(ctx.guild.id), {})
        await storage.panicmode.delete(id=Panic_Cache.get("id"))
        await storage.panicmode.insert(guild_id=ctx.guild.id)
        await self.send_success_embed(ctx, "Panic Mode settings reset.")

async def setup(bot):
    await bot.add_cog(PanicMode(bot))
