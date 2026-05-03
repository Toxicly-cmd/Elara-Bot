import sys

def main():
    with open("Elara/src/commands/utils.py", "r") as f:
        lines = f.readlines()
        
    new_code = """    @commands.hybrid_command(
        name="serverinfo",
        help="Get information about the server",
        aliases=["guildinfo", "si", "gi"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"Server Information: {guild.name}",
            color=0x2b2d31
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # General
        created_at = int(guild.created_at.timestamp())
        general_info = (
            f"**Name:** {guild.name}\\n"
            f"**ID:** `{guild.id}`\\n"
            f"**Owner:** {guild.owner.mention}\\n"
            f"**Created:** <t:{created_at}:R>"
        )
        embed.add_field(name=f"{self.bot.emoji.UTILS} General", value=general_info, inline=True)

        # Members
        humans = len([m for m in guild.members if not m.bot])
        bots = guild.member_count - humans
        members_info = (
            f"**Total:** {guild.member_count}\\n"
            f"**Humans:** {humans}\\n"
            f"**Bots:** {bots}"
        )
        embed.add_field(name=f"{self.bot.emoji.MEMBERS} Members", value=members_info, inline=True)

        # Channels
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        channels_info = (
            f"**Categories:** {categories}\\n"
            f"**Text:** {text_channels}\\n"
            f"**Voice:** {voice_channels}"
        )
        embed.add_field(name=f"{self.bot.emoji.COMMANDS} Channels", value=channels_info, inline=True)

        # Security & Settings
        mfa_level = "Required" if guild.mfa_level == 1 else "None"
        security_info = (
            f"**Verification:** {guild.verification_level.name.capitalize().replace('_', ' ')}\\n"
            f"**MFA Level:** {mfa_level}\\n"
            f"**Filter:** {guild.explicit_content_filter.name.capitalize().replace('_', ' ')}"
        )
        embed.add_field(name=f"{self.bot.emoji.SECURITY} Security", value=security_info, inline=True)

        # Extras
        extras_info = (
            f"**Roles:** {len(guild.roles)}\\n"
            f"**Emojis:** {len(guild.emojis)}\\n"
            f"**Boosts:** {guild.premium_subscription_count} (Level {guild.premium_tier})"
        )
        embed.add_field(name=f"{self.bot.emoji.INFO} Extras", value=extras_info, inline=True)

        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

"""

    start = 4046
    end = 4691
    
    new_lines = lines[:start] + [new_code] + lines[end:]
    
    with open("Elara/src/commands/utils.py", "w") as f:
        f.writelines(new_lines)

main()
