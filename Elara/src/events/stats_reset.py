from __future__ import annotations
import asyncio
import datetime
from discord.ext import commands, tasks
from Elara.console.logging import logger
from Elara.engine.Bot import AutoShardedBot
import storage.member_stats

class StatsReset(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.reset_task.start()

    def cog_unload(self):
        self.reset_task.cancel()

    @tasks.loop(minutes=1)
    async def reset_task(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        
        # Reset Daily at 00:00 UTC
        if now.hour == 0 and now.minute == 0:
            logger.system("Resetting daily member stats...")
            try:
                await storage.member_stats.reset_daily()
                logger.success("Daily member stats reset successfully")
            except Exception as e:
                logger.error(f"Error resetting daily stats: {e}")

        # Reset Weekly on Monday 00:00 UTC
        if now.weekday() == 0 and now.hour == 0 and now.minute == 0:
            logger.system("Resetting weekly member stats...")
            try:
                await storage.member_stats.reset_weekly()
                logger.success("Weekly member stats reset successfully")
            except Exception as e:
                logger.error(f"Error resetting weekly stats: {e}")

async def setup(bot):
    await bot.add_cog(StatsReset(bot))
