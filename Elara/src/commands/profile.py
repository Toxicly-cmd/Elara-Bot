import discord
from discord.ext import commands
import storage.users
from Elara.engine.Bot import AutoShardedBot
from Elara.workflows import ui
import Elara.src.checks.checks as checks

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

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

    @commands.hybrid_command(name="profile", help="Display a user's profile")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def profile(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        user_data = await storage.users.get(user_id=user.id) or {}
        
        # Get data for UI
        avatar_url = user_data.get('custom_avatar') or str(user.display_avatar.url)
        banner_url = user_data.get('custom_banner') or (str(user.banner.url) if user.banner else None)
        bio = user_data.get('bio') or "No bio set."
        badges = user_data.get('badges') or []
        
        # Create UI Profile (using ui.py logic)
        try:
            image = ui.get_ui_profile(
                avatar_url=avatar_url,
                banner_url=banner_url,
                display_name=user.display_name,
                username=user.name,
                userid=str(user.id),
                coin=int(user_data.get('balance', 0)),
                created_at=user.created_at,
                badges=badges
            )
            file = discord.File(image, filename="profile.png")
            embed = discord.Embed(color=0x2b2d31)
            embed.set_image(url="attachment://profile.png")
            embed.set_footer(text=f"Toxic (7ox4) • Profile of @{user.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(file=file, embed=embed)
        except Exception as e:
            await ctx.send(f"Error generating profile: {e}")

    @commands.group(name="bio", help="Manage your profile bio", invoke_without_command=True)
    async def bio(self, ctx, *, text: str = None):
        if ctx.invoked_subcommand is None:
            if not text:
                user_data = await storage.users.get(user_id=ctx.author.id) or {}
                bio = user_data.get('bio') or "No bio set."
                return await ctx.send(f"Your current bio: {bio}")
            await ctx.invoke(self.bio_set, text=text)

    @bio.command(name="set")
    async def bio_set(self, ctx, *, text: str):
        if len(text) > 200:
            return await self.send_denied_embed(ctx, "Bio is too long (max 200 chars).")
        await storage.users.update(user_id=ctx.author.id, bio=text)
        await self.send_success_embed(ctx, "Bio updated successfully.")

    @bio.command(name="clear")
    async def bio_clear(self, ctx):
        await storage.users.update(user_id=ctx.author.id, bio=None)
        await self.send_success_embed(ctx, "Bio cleared.")

    @commands.group(name="badge", help="Manage user badges", invoke_without_command=True)
    async def badge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @badge.command(name="add")
    @commands.is_owner()
    async def badge_add(self, ctx, user: discord.Member, badge_name: str):
        user_data = await storage.users.get(user_id=user.id)
        if not user_data:
            await storage.users.insert(user_id=user.id)
            user_data = await storage.users.get(user_id=user.id)
        
        badges = user_data.get('badges', [])
        if badge_name in badges:
            return await self.send_denied_embed(ctx, "User already has this badge.")
        
        badges.append(badge_name)
        await storage.users.update(user_id=user.id, badges=badges)
        await self.send_success_embed(ctx, f"Added badge `{badge_name}` to {user.mention}.")

    @badge.command(name="remove")
    @commands.is_owner()
    async def badge_remove(self, ctx, user: discord.Member, badge_name: str):
        user_data = await storage.users.get(user_id=user.id)
        if not user_data or badge_name not in user_data.get('badges', []):
            return await self.send_denied_embed(ctx, "User does not have this badge.")
        
        badges = user_data.get('badges')
        badges.remove(badge_name)
        await storage.users.update(user_id=user.id, badges=badges)
        await self.send_success_embed(ctx, f"Removed badge `{badge_name}` from {user.mention}.")

    @badge.command(name="list")
    async def badge_list(self, ctx):
        # List available badges (this would ideally come from a config)
        badges = ["developer", "staff", "early_supporter", "premium", "donator"]
        await ctx.send(f"Available badges: {', '.join(badges)}")

    @commands.group(name="customize", help="Customize your profile branding", invoke_without_command=True)
    async def customize(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @customize.command(name="avatar")
    async def customize_avatar(self, ctx, url: str):
        await storage.users.update(user_id=ctx.author.id, custom_avatar=url)
        await self.send_success_embed(ctx, "Custom profile avatar set.")

    @customize.command(name="banner")
    async def customize_banner(self, ctx, url: str):
        await storage.users.update(user_id=ctx.author.id, custom_banner=url)
        await self.send_success_embed(ctx, "Custom profile banner set.")

    @customize.command(name="bio")
    async def customize_bio(self, ctx, *, text: str):
        await ctx.invoke(self.bio_set, text=text)

    @customize.command(name="reset")
    async def customize_reset(self, ctx):
        await storage.users.update(user_id=ctx.author.id, custom_avatar=None, custom_banner=None, bio=None)
        await self.send_success_embed(ctx, "Profile branding reset to default.")

async def setup(bot):
    await bot.add_cog(Profile(bot))
