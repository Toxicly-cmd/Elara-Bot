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
            title=f"Server Information",
            color=color.black
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        created_at = int(guild.created_at.timestamp())
        
        # Sleek Premium Description with Animated Crown and Emojis
        embed.description = (
            f"**{guild.name}** was created on <t:{created_at}:F> (<t:{created_at}:R>)\\n\\n"
            f"<a:neo_Crown:1498047758509150379> **Owner:** {guild.owner.mention} (`{guild.owner.id}`)\\n"
            f"{self.bot.emoji.GUILD} **Server ID:** `{guild.id}`\\n"
            f"{self.bot.emoji.PREMIUM} **Boost Status:** Level {guild.premium_tier} ({guild.premium_subscription_count} Boosts)"
        )

        humans = len([m for m in guild.members if not m.bot])
        bots = guild.member_count - humans
        
        # Premium Blockquote Design
        members_info = (
            f">>> **Total:** `{guild.member_count}`\\n"
            f"**Humans:** `{humans}`\\n"
            f"**Bots:** `{bots}`"
        )
        embed.add_field(name=f"{self.bot.emoji.MEMBER} Members", value=members_info, inline=True)

        channels_info = (
            f">>> **Text:** `{len(guild.text_channels)}`\\n"
            f"**Voice:** `{len(guild.voice_channels)}`\\n"
            f"**Categories:** `{len(guild.categories)}`"
        )
        embed.add_field(name=f"{self.bot.emoji.CHANNEL} Channels", value=channels_info, inline=True)

        # Empty Field for Alignment
        embed.add_field(name="\\u200b", value="\\u200b", inline=True)

        mfa_level = "Required" if guild.mfa_level == 1 else "None"
        security_info = (
            f">>> **Verification:** `{guild.verification_level.name.capitalize()}`\\n"
            f"**MFA Requirement:** `{mfa_level}`\\n"
            f"**Content Filter:** `{guild.explicit_content_filter.name.capitalize().replace('_', ' ')}`"
        )
        embed.add_field(name=f"{self.bot.emoji.SECURITY} Security", value=security_info, inline=True)
        
        extras_info = (
            f">>> **Roles:** `{len(guild.roles)}`\\n"
            f"**Emojis:** `{len(guild.emojis)}`\\n"
            f"**Stickers:** `{len(guild.stickers)}`"
        )
        embed.add_field(name=f"{self.bot.emoji.INFO} Extras", value=extras_info, inline=True)

        # Empty Field for Alignment
        embed.add_field(name="\\u200b", value="\\u200b", inline=True)

        embed.set_footer(text=f"Elara • Requested by {ctx.author.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

"""

    start = 3969 # line 3970 is index 3969
    end = 4614   # line 4615 is index 4614
    
    new_lines = lines[:start] + [new_code] + lines[end:]
    
    with open("Elara/src/commands/utils.py", "w") as f:
        f.writelines(new_lines)

main()
