
import sys
import os

# Add the project root to sys.path
sys.path.append('/Users/toxic/Documents/Elara panel/Elara-Bot')

from Elara.style import urls, emoji
from Elara.config.config import BotConfigClass

class MockBot:
    def __init__(self):
        self.urls = urls
        self.emoji = emoji
        self.BotConfig = BotConfigClass()
        self.user = type('User', (), {'name': 'Elara', 'display_avatar': type('Avatar', (), {'url': 'http://avatar.url'})()})()

class MockCtx:
    def __init__(self):
        self.author = type('Author', (), {'name': 'Toxic'})()

bot = MockBot()
ctx = MockCtx()

try:
    prefix = bot.BotConfig.PREFIX
    description = (
        f"**Hey {ctx.author.name}**, welcome to **Elara** {bot.emoji.BOT}\n"
        f"I am a versatile Discord bot designed to provide you with the best experience. "
        f"Use the menu below to explore my diverse categories and commands.\n\n"
        f"{bot.emoji.INFO} **Quick Stats**\n"
        f"> **Commands:** `0` Available\n"
        f"> **Prefix:** `{bot.BotConfig.PREFIX}`\n"
        f"> **Developer:** `7ox4`\n\n"
        f"{bot.emoji.LINK} **Resources**\n"
        f"> [Invite]({bot.urls.INVITE}) • [Support]({bot.urls.SUPPORT}) • [Website]({bot.urls.WEBSITE})\n"
    )
    print("Formatting successful!")
    print(description)
except Exception as e:
    print(f"Formatting failed: {e}")
