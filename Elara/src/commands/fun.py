from __future__ import annotations
import discord


from discord.ext import commands


import Elara.src.checks.checks as checks


from Elara.console.logging import logger


from Elara.style import color


from Elara.utils import pings


from Elara.workflows import gif


from Elara.engine.Bot import AutoShardedBot


from Elara.workflows import ui


import random


import traceback


import asyncio


class Fun(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

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

    async def cog_check(self, ctx: commands.Context):
        if ctx.command.name in ["horny", "gay", "lesbian"]:
            return True
        if await self.bot.is_owner(ctx.author):
            return True
        result = checks.has_fun_access_predicate(ctx)
        if not result:
            raise commands.CheckFailure("You are restricted from using Fun commands.")
        return True

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            return await self.send_denied_embed(ctx, str(error))
        
        # Log other errors
        logger.error(f"Error in Fun Cog: {error}")
        traceback.print_exc()

        class cog_info:

            name = "Fun"

            category = "Extra"

            description = "Fun commands"

            hidden = False

            emoji = self.bot.emoji.FUN

        self.cog_info = cog_info

    @commands.command(name="slap", help="Slap a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def slap(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get slap gif

        image_url = gif.get_gif("slapping")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** slapped **{(user.name) if user.id != ctx.author.id else 'themselves'}** {self.bot.emoji.SLAP}",
            color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="hug", help="Hug a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def hug(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get hug gif

        image_url = gif.get_gif("hugging")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** hugged **{(user.name) if user.id != ctx.author.id else 'themselves'}** {self.bot.emoji.HUG}",
            color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="kiss", help="Kiss a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def kiss(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get kiss gif

        image_url = gif.get_gif("kissing")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** kissed **{(user.name) if user.id != ctx.author.id else 'themselves'}** {self.bot.emoji.KISS}",
            color=0x2b2d31,
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="pat", help="Pat a person")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def pat(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get pat gif

        image_url = gif.get_gif("patting")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** patted **{(user.name) if user.id != ctx.author.id else 'themselves'}** {self.bot.emoji.PAT}",
            color=0x2b2d31,
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="cry", help="Cry")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def cry(self, ctx: commands.Context):

        # get cry gif

        image_url = gif.get_gif("crying")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is crying {self.bot.emoji.CRY}", color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="dance", help="Dance")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def dance(self, ctx: commands.Context):

        # get dance gif

        image_url = gif.get_gif("dancing")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is dancing {self.bot.emoji.DANCE}", color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="laugh", help="Laugh")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def laugh(self, ctx: commands.Context):

        # get laugh gif

        image_url = gif.get_gif("laughing")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is laughing {self.bot.emoji.LAUGH}", color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="smile", help="Smile")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def smile(self, ctx: commands.Context):

        # get smile gif

        image_url = gif.get_gif("smiling")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is smiling {self.bot.emoji.SMILE}", color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="angry", help="Angry")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def angry(self, ctx: commands.Context, user: discord.User = None):

        if not user:

            user = ctx.author

        # get angry gif

        image_url = gif.get_gif("angry")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is angry at **{(user.name) if user.id != ctx.author.id else 'themselves'}** {self.bot.emoji.ANGRY}",
            color=0x2b2d31,
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="confused", help="Confused")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def confused(self, ctx: commands.Context):

        # get confused gif

        image_url = gif.get_gif("confused")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is confused {self.bot.emoji.CONFUSED}", color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="sleep", help="Sleep")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def sleep(self, ctx: commands.Context):

        # get sleep gif

        image_url = gif.get_gif("sleeping cartoon")

        embed = discord.Embed(
            description=f"**{ctx.author.name}** is sleeping {self.bot.emoji.SLEEP}", color=0x2b2d31
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    async def do_action(self, ctx, name, action_text, emoji):
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            desc = f"**{ctx.author.name}** {action_text} **{user.name}** {emoji}"
        else:
            desc = f"**{ctx.author.name}** is {name}ing {emoji}"
        
        image_url = gif.get_gif(f"anime {name}")
        embed = discord.Embed(description=desc, color=0x2b2d31)
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="nom")
    async def nom(self, ctx): await self.do_action(ctx, "nom", "noms", self.bot.emoji.FUN)

    @commands.command(name="poke")
    async def poke(self, ctx): await self.do_action(ctx, "poke", "poked", self.bot.emoji.FUN)

    @commands.command(name="stare")
    async def stare(self, ctx): await self.do_action(ctx, "stare", "is staring at", self.bot.emoji.FUN)

    @commands.command(name="highfive")
    async def highfive(self, ctx): await self.do_action(ctx, "highfive", "high-fived", self.bot.emoji.FUN)

    @commands.command(name="bite")
    async def bite(self, ctx): await self.do_action(ctx, "bite", "bit", self.bot.emoji.FUN)

    @commands.command(name="punch")
    async def punch(self, ctx): await self.do_action(ctx, "punch", "punched", self.bot.emoji.FUN)

    @commands.command(name="handholding")
    async def handholding(self, ctx): await self.do_action(ctx, "handholding", "is holding hands with", self.bot.emoji.FUN)

    @commands.command(name="tickle")
    async def tickle(self, ctx): await self.do_action(ctx, "tickle", "tickled", self.bot.emoji.FUN)

    @commands.command(name="wave")
    async def wave(self, ctx): await self.do_action(ctx, "wave", "waved at", self.bot.emoji.FUN)

    @commands.command(name="snuggle")
    async def snuggle(self, ctx): await self.do_action(ctx, "snuggle", "snuggled with", self.bot.emoji.FUN)

    @commands.command(name="blush")
    async def blush(self, ctx): await self.do_action(ctx, "blush", "is blushing at", self.bot.emoji.FUN)

    @commands.command(name="pout")
    async def pout(self, ctx): await self.do_action(ctx, "pout", "pouts at", self.bot.emoji.FUN)

    @commands.command(name="shrug")
    async def shrug(self, ctx): await self.do_action(ctx, "shrug", "shrugs at", self.bot.emoji.FUN)

    @commands.command(name="smug")
    async def smug(self, ctx): await self.do_action(ctx, "smug", "is smug at", self.bot.emoji.FUN)

    @commands.command(name="thumbsup")
    async def thumbsup(self, ctx): await self.do_action(ctx, "thumbsup", "gives a thumbs up to", self.bot.emoji.FUN)

    @commands.command(name="thinking")
    async def thinking(self, ctx): await self.do_action(ctx, "thinking", "is thinking about", self.bot.emoji.FUN)

    @commands.command(name="happy")
    async def happy(self, ctx): await self.do_action(ctx, "happy", "is happy with", self.bot.emoji.FUN)

    @commands.command(name="cuddle")
    async def cuddle(self, ctx): await self.do_action(ctx, "cuddle", "cuddled with", self.bot.emoji.FUN)

    @commands.command(name="scoff")
    async def scoff(self, ctx): await self.do_action(ctx, "scoff", "scoffs at", self.bot.emoji.FUN)

    @commands.command(name="pray")
    async def pray(self, ctx): await self.do_action(ctx, "pray", "is praying for", self.bot.emoji.FUN)

    @commands.command(name="gay", help="Predict a persons gayness level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def gay_command(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            gayness = random.randint(0, 100)

            if user.id == 1219917329270571038:

                gayness = random.randint(0, 9)

            elif any(user.id == dev.id for dev in self.bot.developers):

                gayness = 0

            elif user.id in [
                1044145477660201000,
                1396460502464593963
            ]:

                gayness = 100

            embed = discord.Embed(
                description=f"**Gay Level** {self.bot.emoji.FUN}\n**{user.name}** is `{gayness}%` Gay",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="lesbian", help="Predict a persons lesbian level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def lesbian(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            lasbian = random.randint(0, 100)

            if user.id == 1219917329270571038:

                lasbian = random.randint(0, 9)

            elif any(user.id == dev.id for dev in self.bot.developers):

                lasbian = 0

            elif user.id in [
                1396460502464593963,
                1349068185545998437
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                lasbian = 100

            embed = discord.Embed(
                description=f"**Lesbian Level** {self.bot.emoji.FUN}\n**{user.name}** is `{lasbian}%` Lesbian",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="horny", help="Predict a persons horny level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def horny(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            horny = random.randint(0, 100)

            if user.id == 1219917329270571038:
                horny = random.randint(0, 9)

            elif any(user.id == dev.id for dev in self.bot.developers):

                horny = 0

            elif user.id in [
                1396460502464593963
            ]:
                horny = 100

            embed = discord.Embed(
                description=f"**Horny Level** {self.bot.emoji.FUN}\n**{user.name}** is `{horny}%` Horny",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="simp", help="Predict a persons simp level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def simp(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            simp = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                simp = 0

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                simp = 100

            embed = discord.Embed(
                description=f"**Simp Level** {self.bot.emoji.FUN}\n{user.mention} is `{simp}%` Simp",
                color=0x2b2d31,
            )

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="iq", help="Predict a persons IQ level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def iq(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            iq = random.randint(0, 200)

            if any(user.id == dev.id for dev in self.bot.developers):

                iq = 200

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                iq = 0

            embed = discord.Embed(
                description=f"**IQ Level** {self.bot.emoji.FUN}\n{user.mention} has an IQ of `{iq}`",
                color=0x2b2d31,
            )

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="cute", help="Predict a persons cuteness level")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def cute(self, ctx: commands.Context, user: discord.Member = None):

        try:

            if not user:

                user = ctx.author

            cute = random.randint(0, 100)

            if any(user.id == dev.id for dev in self.bot.developers):

                cute = 100

            elif user.id in [
                # 850031806795219014,
                # 1062994575058276373,
                # 791348920324063273,
                # 224611733032009729
            ]:

                cute = 0

            embed = discord.Embed(
                description=f"**Cute Level** {self.bot.emoji.FUN}\n{user.mention} is `{cute}%` Cute",
                color=0x2b2d31,
            )

            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


    @commands.command(
        name="ship",
        help="Predict a relationship between two persons",
        aliases=["compatibility", "romance"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=4, per=60, type=commands.BucketType.user)
    async def relation(
        self, ctx: commands.Context, user1: discord.Member, user2: discord.Member = None
    ):
        try:
            if not user2:
                user1, user2 = ctx.author, user1

            percentage = random.randint(0, 100)
            if any(u.id == dev.id for u in [user1, user2] for dev in self.bot.developers):
                percentage = 0

            embed = discord.Embed(
                description=f"{user1.mention} and {user2.mention} are `{percentage}%` Compatible",
                color=0x2b2d31,
            )
            embed.set_author(name="Relationship Percentage", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)

            file = None
            try:
                image = ui.create_relation_percentage_banner(user1.display_avatar.url, user2.display_avatar.url, percentage)
                file = discord.File(image, filename="relationship.png")
                embed.set_image(url="attachment://relationship.png")
            except Exception as e:
                logger.error(f"Error creating relation banner: {e}")

            await ctx.send(embed=embed, file=file)
        except Exception as e:
            logger.error(f"Error in relation command: {e}")
            traceback.print_exc()

    @commands.command(name="truth", help="Get a truth question")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def truth(self, ctx: commands.Context):
        questions = [
            "What is your biggest fear?",
            "What is the most embarrassing thing you've ever done?",
            "What is your biggest secret?",
            "What is the most trouble you've ever been in?",
            "What is your biggest regret?",
            "Who is your crush?",
            "What is the most expensive thing you've ever bought?",
            "What is your dream job?",
            "What is your favorite movie?",
            "What is your favorite song?",
            "If you could travel anywhere in the world, where would you go?",
            "What is the most daring thing you've ever done?",
            "What is your favorite childhood memory?",
            "What is the best piece of advice you've ever received?",
            "What is your favorite hobby?",
            "What is your favorite food?",
            "What is your favorite book?",
            "What is your favorite sport?",
            "What is your favorite color?",
            "What is your favorite animal?"
        ]
        question = random.choice(questions)
        embed = discord.Embed(
            description=f"**Truth** {self.bot.emoji.FUN}\n> {question}",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="dare", help="Get a dare task")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def dare(self, ctx: commands.Context):
        tasks = [
            "Do 20 pushups.",
            "Sing a song loudly.",
            "Dance for 1 minute.",
            "Tell a joke.",
            "Call a random person and say hello.",
            "Send a funny picture to your crush.",
            "Eat a spoonful of hot sauce.",
            "Wear your clothes inside out for the rest of the day.",
            "Do a handstand for 10 seconds.",
            "Talk in an accent for the next 10 minutes.",
            "Post an embarrassing photo on social media.",
            "Drink a glass of water without using your hands.",
            "Try to touch your nose with your tongue.",
            "Do 50 jumping jacks.",
            "Say the alphabet backwards as fast as you can.",
            "Spin around 10 times and then try to walk in a straight line.",
            "Make a funny face and take a selfie.",
            "Write a poem about a random object in the room.",
            "Do a cartwheel.",
            "Tell a scary story."
        ]
        task = random.choice(tasks)
        embed = discord.Embed(
            description=f"**Dare** {self.bot.emoji.FUN}\n> {task}",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.group(name="marriage", help="Marriage related commands", invoke_without_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def marriage(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.invoked_subcommand is None:
            if not user:
                user = ctx.author
            
            data = await storage.marriage.get_marriage(user.id)
            if not data:
                embed = discord.Embed(
                    description=f"**Marriage Status** {self.bot.emoji.FUN}\n> {user.mention} is currently **Single**.",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
                return await ctx.send(embed=embed)
            
            partner_id = data['user2_id'] if data['user1_id'] == user.id else data['user1_id']
            partner = self.bot.get_user(partner_id) or await self.bot.fetch_user(partner_id)
            
            embed = discord.Embed(
                description=(
                    f"**Marriage Status** {self.bot.emoji.FUN}\n"
                    f"> **Partner:** {partner.mention}\n"
                    f"> **Married:** <t:{int(data['timestamp'].timestamp())}:R>"
                ),
                color=0x2b2d31
            )
            embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

    @marriage.command(name="propose", help="Propose to a user", aliases=["marry"])
    @checks.ignore_check()
    @checks.blacklist_check()
    async def propose(self, ctx: commands.Context, user: discord.Member):
        if user.id == ctx.author.id:
            return await self.send_denied_embed(ctx, "You cannot marry yourself.")
        
        if user.bot:
            return await self.send_denied_embed(ctx, "You cannot marry a bot.")
        
        # Check if author is already married
        author_data = await storage.marriage.get_marriage(ctx.author.id)
        if author_data:
            return await self.send_denied_embed(ctx, "You are already married.")
        
        # Check if user is already married
        user_data = await storage.marriage.get_marriage(user.id)
        if user_data:
            return await self.send_denied_embed(ctx, f"{user.mention} is already married.")
        
        class MarriageView(discord.ui.View):
            def __init__(self, bot, author, target):
                super().__init__(timeout=60)
                self.bot = bot
                self.author = author
                self.target = target
            
            @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != self.target.id:
                    return await interaction.response.send_message("This proposal is not for you.", ephemeral=True)
                
                await storage.marriage.marry(self.author.id, self.target.id)
                embed = discord.Embed(
                    description=f"**Marriage Accepted!** {self.bot.emoji.SUCCESS}\n> {self.author.mention} and {self.target.mention} are now married!",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{self.author.name}", icon_url=self.bot.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=None)
            
            @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
            async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != self.target.id:
                    return await interaction.response.send_message("This proposal is not for you.", ephemeral=True)
                
                embed = discord.Embed(
                    description=f"**Marriage Declined** {self.bot.emoji.ERROR}\n> {self.target.mention} declined the proposal from {self.author.mention}.",
                    color=0x2b2d31
                )
                embed.set_footer(text=f"Toxic (7ox4) • Action by @{self.author.name}", icon_url=self.bot.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=None)

        embed = discord.Embed(
            description=f"**Marriage Proposal** {self.bot.emoji.FUN}\n> {user.mention}, {ctx.author.mention} has proposed to you!",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed, view=MarriageView(self.bot, ctx.author, user))

    @commands.command(name="marry", help="Marry a user")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def marry_top(self, ctx: commands.Context, user: discord.Member):
        await ctx.invoke(self.propose, user=user)

    @marriage.command(name="divorce", help="Divorce your partner")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def divorce(self, ctx: commands.Context):
        data = await storage.marriage.get_marriage(ctx.author.id)
        if not data:
            return await self.send_denied_embed(ctx, "You are not married.")
        
        await storage.marriage.divorce(ctx.author.id)
        partner_id = data['user2_id'] if data['user1_id'] == ctx.author.id else data['user1_id']
        partner = self.bot.get_user(partner_id) or await self.bot.fetch_user(partner_id)
        
        embed = discord.Embed(
            description=f"**Divorce Successful** {self.bot.emoji.SUCCESS}\n> You have divorced {partner.mention}.",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Toxic (7ox4) • Action by @{ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="mydog", aliases=["dog"])
    async def mydog(self, ctx):
        async with self.bot.session.get("https://dog.ceo/api/breeds/image/random") as r:
            data = await r.json()
            embed = discord.Embed(color=0x2b2d31)
            embed.set_image(url=data['message'])
            await ctx.send(embed=embed)

    @commands.command(name="cat")
    async def cat(self, ctx):
        async with self.bot.session.get("https://api.thecatapi.com/v1/images/search") as r:
            data = await r.json()
            embed = discord.Embed(color=0x2b2d31)
            embed.set_image(url=data[0]['url'])
            await ctx.send(embed=embed)

    @commands.command(name="joke")
    async def joke(self, ctx):
        async with self.bot.session.get("https://v2.jokeapi.dev/joke/Any?type=single") as r:
            data = await r.json()
            joke = data.get('joke', 'No joke found.')
            embed = discord.Embed(description=f"**Joke** {self.bot.emoji.FUN}\n> {joke}", color=0x2b2d31)
            await ctx.send(embed=embed)


    @commands.command(name="eightball", aliases=["8ball"])
    async def eightball(self, ctx, *, question: str):
        responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = discord.Embed(description=f"**8ball** {self.bot.emoji.FUN}\n**Q:** {question}\n**A:** {random.choice(responses)}", color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.command(name="pickup")
    async def pickup(self, ctx):
        async with self.bot.session.get("https://vincent0624.github.io/programming-pick-up-lines/lines.json") as r:
             # Fallback to a hardcoded list if the API is complex or unavailable
             lines = ["Are you a keyboard? Because you're just my type.", "Are you a Wi-Fi signal? Because I'm feeling a connection.", "Is your name Google? Because you have everything I’m searching for."]
             line = random.choice(lines)
             embed = discord.Embed(description=f"**Pickup Line** {self.bot.emoji.FUN}\n> {line}", color=0x2b2d31)
             await ctx.send(embed=embed)

    @commands.command(name="showerthought")
    async def showerthought(self, ctx):
        async with self.bot.session.get("https://www.reddit.com/r/showerthoughts/random.json", headers={'User-agent': 'Elara Bot'}) as r:
            data = await r.json()
            thought = data[0]['data']['children'][0]['data']['title']
            embed = discord.Embed(description=f"**Shower Thought** {self.bot.emoji.FUN}\n> {thought}", color=0x2b2d31)
            await ctx.send(embed=embed)

    @commands.command(name="hack")
    async def hack(self, ctx, user: discord.Member):
        msg = await ctx.send(f"Hacking {user.name}...")
        await asyncio.sleep(1)
        await msg.edit(content="Finding email address...")
        await asyncio.sleep(1)
        await msg.edit(content=f"Email: {user.name.lower().replace(' ', '')}@gmail.com")
        await asyncio.sleep(1)
        await msg.edit(content="Finding password...")
        await asyncio.sleep(1)
        await msg.edit(content="Password: " + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10)))
        await asyncio.sleep(1)
        await msg.edit(content="Hacking social media accounts...")
        await asyncio.sleep(1)
        await msg.edit(content="Finding most used word...")
        await asyncio.sleep(1)
        await msg.edit(content="Most used word: 'noob'")
        await asyncio.sleep(1)
        await msg.edit(content=f"Successfully hacked {user.name}!")

    @commands.command(name="token")
    async def token(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        token = "MTA" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=20)) + "." + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6)) + "." + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=27))
        embed = discord.Embed(description=f"**{user.name}'s Token**\n`{token}`", color=0x2b2d31)
        await ctx.send(embed=embed)

async def setup(bot: AutoShardedBot):
    await bot.add_cog(Fun(bot))

