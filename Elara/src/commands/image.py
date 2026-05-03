import discord
from discord.ext import commands
import aiohttp
from io import BytesIO
from Elara.engine.Bot import AutoShardedBot

class ImageManipulation(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot
        self.alex_api = "https://api.alexflipnote.dev"
        self.nekobot_api = "https://nekobot.xyz/api/imagegen"

    async def get_image_bytes(self, url, params=None):
        async with self.bot.session.get(url, params=params) as r:
            if r.status_code != 200:
                return None
            return await r.read()

    async def send_image_api(self, ctx, url, params, filename="image.png"):
        async with ctx.typing():
            data = await self.get_image_bytes(url, params)
            if not data:
                return await ctx.send("Failed to generate image.")
            file = discord.File(BytesIO(data), filename=filename)
            await ctx.send(file=file)

    @commands.command(name="biden")
    async def biden(self, ctx, *, text: str):
        await self.send_image_api(ctx, f"{self.alex_api}/biden", {"text": text})

    @commands.command(name="pikachu")
    async def pikachu(self, ctx, *, text: str):
        await self.send_image_api(ctx, f"{self.alex_api}/pikachu", {"text": text})

    @commands.command(name="drake")
    async def drake(self, ctx, text1: str, text2: str):
        await self.send_image_api(ctx, f"{self.alex_api}/drake", {"top": text1, "bottom": text2})

    @commands.command(name="pooh")
    async def pooh(self, ctx, text1: str, text2: str):
        await self.send_image_api(ctx, f"{self.alex_api}/pooh", {"text1": text1, "text2": text2})

    @commands.command(name="sadcat")
    async def sadcat(self, ctx, *, text: str):
        await self.send_image_api(ctx, f"{self.alex_api}/sadcat", {"text": text})

    @commands.command(name="oogway")
    async def oogway(self, ctx, *, text: str):
        # Placeholder or different API if available
        await ctx.send(f"Oogway says: {text}")

    @commands.command(name="blur")
    async def blur(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.alex_api}/filter/blur", {"image": str(user.display_avatar.url)})

    @commands.command(name="invert")
    async def invert(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.alex_api}/filter/invert", {"image": str(user.display_avatar.url)})

    @commands.command(name="greyscale")
    async def greyscale(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.alex_api}/filter/b&w", {"image": str(user.display_avatar.url)})

    @commands.command(name="clown")
    async def clown(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.alex_api}/filter/clown", {"image": str(user.display_avatar.url)})

    @commands.command(name="jail")
    async def jail(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.nekobot_api}", {"type": "jail", "url": str(user.display_avatar.url)})

    @commands.command(name="wanted")
    async def wanted(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.nekobot_api}", {"type": "wanted", "url": str(user.display_avatar.url)})

    @commands.command(name="spank")
    async def spank(self, ctx, user: discord.Member):
        await self.send_image_api(ctx, f"{self.nekobot_api}", {"type": "spank", "user1": str(ctx.author.display_avatar.url), "user2": str(user.display_avatar.url)})

    @commands.command(name="trash")
    async def trash(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await self.send_image_api(ctx, f"{self.nekobot_api}", {"type": "trash", "url": str(user.display_avatar.url)})

    @commands.command(name="supreme")
    async def supreme(self, ctx, *, text: str):
        await self.send_image_api(ctx, f"{self.alex_api}/supreme", {"text": text})

    @commands.command(name="didyoumean")
    async def didyoumean(self, ctx, text1: str, text2: str):
        await self.send_image_api(ctx, f"{self.alex_api}/didyoumean", {"top": text1, "bottom": text2})

    @commands.command(name="reverse")
    async def reverse(self, ctx, *, text: str):
        await ctx.send(text[::-1])

    @commands.command(name="mock")
    async def mock(self, ctx, *, text: str):
        await ctx.send("".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text)))

    @commands.command(name="morse")
    async def morse(self, ctx, *, text: str):
        MORSE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': ' '}
        await ctx.send(" ".join(MORSE_DICT.get(c.upper(), c) for c in text))

    @commands.command(name="doublestruck")
    async def doublestruck(self, ctx, *, text: str):
        mapping = {'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 'f': '𝕗', 'g': '𝕘', 'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 'k': '𝕜', 'l': '𝕝', 'm': '𝕞', 'n': '𝕟', 'o': '𝕠', 'p': '𝕡', 'q': '𝕢', 'r': '𝕣', 's': '𝕤', 't': '𝕥', 'u': '𝕦', 'v': '𝕧', 'w': '𝕨', 'x': '𝕩', 'y': '𝕪', 'z': '𝕫', 'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 'F': '𝔽', 'G': '𝔾', 'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 'K': '𝕂', 'L': '𝕃', 'M': '𝕄', 'N': 'ℕ', 'O': '𝕆', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋', 'U': '𝕌', 'V': '𝕍', 'W': '𝕎', 'X': '𝕏', 'Y': '𝕐', 'Z': 'ℤ', '0': '𝟘', '1': '𝟙', '2': '𝟚', '3': '𝟛', '4': '𝟜', '5': '𝟝', '6': '𝟞', '7': '𝟟', '8': '𝟠', '9': '𝟡'}
        await ctx.send("".join(mapping.get(c, c) for c in text))

    @commands.command(name="emojipasta")
    async def emojipasta(self, ctx, *, text: str):
        emojis = ["😂", "😩", "🔥", "💯", "💀", "💅", "✨", "👀", "🙌", "👏", "😤", "🤫", "🥶", "🥵"]
        words = text.split()
        await ctx.send(" ".join(f"{word} {random.choice(emojis)}" if random.random() > 0.5 else word for word in words))

    @commands.command(name="fhelp")
    async def fhelp(self, ctx):
        embed = discord.Embed(title="Fun & Image Help", description="List of all fun and image manipulation commands.", color=0x2b2d31)
        embed.add_field(name="Action", value="`hug`, `kiss`, `slap`, `pat`, `cry`, `dance`, `smile`, `nom`, `poke`, `stare`, `highfive`, `bite`, `punch`, `tickle`, `wave`, `snuggle`, `blush`, `pout`, `shrug`, `smug`, `thumbsup`, `thinking`, `happy`, `cuddle`, `scoff`, `pray`")
        embed.add_field(name="Memes", value="`biden`, `pikachu`, `drake`, `pooh`, `sadcat`, `oogway`, `jail`, `wanted`, `spank`, `trash`, `clown`, `supreme`, `didyoumean`")
        embed.add_field(name="Filters", value="`blur`, `invert`, `greyscale`")
        embed.add_field(name="Random", value="`mydog`, `cat`, `joke`, `fact`, `8ball`, `pickup`, `showerthought`")
        embed.add_field(name="Text", value="`reverse`, `mock`, `morse`")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ImageManipulation(bot))
