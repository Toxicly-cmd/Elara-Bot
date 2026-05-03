import discord
from discord.ext import commands
import storage
from Elara.memory.cache import cache
import Elara.src.checks.checks as checks

class MainRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_success_embed(self, ctx, description):
        embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS} {description}", color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.group(name="mainrole", help="Main role management", invoke_without_command=True)
    async def mainrole_group(self, ctx):
        await ctx.send_help(ctx.command)

    @mainrole_group.command(name="add")
    async def mainrole_add(self, ctx, role: discord.Role):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Mainrole_Cache = cache.mainrole.get(str(ctx.guild.id), {})
        if not Mainrole_Cache:
            await storage.mainrole.insert(guild_id=ctx.guild.id, role_id=role.id)
        else:
            await storage.mainrole.update(id=Mainrole_Cache.get("id"), guild_id=ctx.guild.id, role_id=role.id)
        await self.send_success_embed(ctx, f"Main role set to {role.mention}")

    @mainrole_group.command(name="remove")
    async def mainrole_remove(self, ctx):
        if not await checks.check_is_moderator_permissions(ctx, "administrator"): return
        Mainrole_Cache = cache.mainrole.get(str(ctx.guild.id), {})
        if Mainrole_Cache:
            await storage.mainrole.delete(id=Mainrole_Cache.get("id"))
        await self.send_success_embed(ctx, "Main role removed")

    @mainrole_group.command(name="reset")
    async def mainrole_reset(self, ctx):
        await self.mainrole_remove(ctx)

    @mainrole_group.command(name="show")
    async def mainrole_show(self, ctx):
        Mainrole_Cache = cache.mainrole.get(str(ctx.guild.id), {})
        if not Mainrole_Cache or not Mainrole_Cache.get("role_id"):
            return await ctx.send("No main role set for this server.")
        role = ctx.guild.get_role(Mainrole_Cache.get("role_id"))
        await ctx.send(f"The main role for this server is: {role.mention if role else 'Unknown Role (Deleted)'}")

async def setup(bot):
    await bot.add_cog(MainRole(bot))
