from __future__ import annotations
import discord
import asyncio
import datetime
from discord.ext import commands
from Elara.console.logging import logger
import storage.member_stats
from Elara.memory.cache import cache

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {} # guild_id -> {code: uses}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initialize_cache()

    async def initialize_cache(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            try:
                if guild.me.guild_permissions.manage_guild:
                    invites = await guild.invites()
                    self.invite_cache[guild.id] = {i.code: i.uses for i in invites}
            except Exception as e:
                logger.warning(f"Failed to cache invites for guild {guild.id}: {e}")

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.guild.id not in self.invite_cache:
            self.invite_cache[invite.guild.id] = {}
        self.invite_cache[invite.guild.id][invite.code] = invite.uses

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if invite.guild.id in self.invite_cache:
            self.invite_cache[invite.guild.id].pop(invite.code, None)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        try:
            if guild.me.guild_permissions.manage_guild:
                invites = await guild.invites()
                self.invite_cache[guild.id] = {i.code: i.uses for i in invites}
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return

        guild = member.guild
        inviter = None
        
        try:
            if guild.me.guild_permissions.manage_guild:
                new_invites = await guild.invites()
                old_invites = self.invite_cache.get(guild.id, {})
                
                for invite in new_invites:
                    if invite.code in old_invites:
                        if invite.uses > old_invites[invite.code]:
                            inviter = invite.inviter
                            break
                    elif invite.uses > 0:
                        inviter = invite.inviter
                        break
                
                # Update cache
                self.invite_cache[guild.id] = {i.code: i.uses for i in new_invites}
        except Exception as e:
            logger.error(f"Error detecting inviter in {guild.id}: {e}")

        if inviter and not inviter.bot:
            # Increment inviter stats
            await storage.member_stats.increment(inviter.id, guild.id, "invites_total")
            
            # Check for fake (account age < 3 days)
            account_age = (datetime.datetime.now(tz=datetime.timezone.utc) - member.created_at).days
            if account_age < 3:
                await storage.member_stats.increment(inviter.id, guild.id, "invites_fake")
            else:
                await storage.member_stats.increment(inviter.id, guild.id, "invites_regular")
            
            # Store who invited the member
            await storage.member_stats.update_member_stats(
                user_id=member.id,
                guild_id=guild.id,
                invited_by=inviter.id
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot:
            return
            
        stats = await storage.member_stats.get(user_id=member.id, guild_id=member.guild.id)
        if stats and stats.get('invited_by'):
            inviter_id = stats.get('invited_by')
            # Increment leave counter for the inviter
            await storage.member_stats.increment(inviter_id, member.guild.id, "invites_leaves")
            # Decrement regular count (total usually stays as "all time history")
            await storage.member_stats.increment(inviter_id, member.guild.id, "invites_regular", delta=-1)

async def setup(bot):
    await bot.add_cog(Invites(bot))
