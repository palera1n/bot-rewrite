import discord
import os
import platform
import psutil

from discord import app_commands
from discord.utils import format_dt
from datetime import datetime
from math import floor

from utils import Cog

class Stats(Cog):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()


    @app_commands.command()
    async def stats(self, ctx: discord.Interaction) -> None:
        process = psutil.Process(os.getpid())

        embed = discord.Embed(
            title=f"{self.bot.user.name} Statistics", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="Bot started", value=format_dt(
            self.start_time, style='R'))
        embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%")
        embed.add_field(name="Memory Usage",
                        value=f"{floor(process.memory_info().rss/1000/1000)} MB")
        embed.add_field(name="Python Version", value=platform.python_version())

        await ctx.response.send_message(embed=embed)

    @app_commands.command()
    async def serverinfo(self, ctx: discord.Interaction):
        guild = ctx.guild
        embed = discord.Embed(title="Server Information",
                              color=discord.Color.blurple())
        embed.set_thumbnail(url=guild.icon)

        if guild.banner is not None:
            embed.set_image(url=guild.banner.url)

        embed.add_field(name="Users", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(
            guild.channels) + len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Bans", value=len(
            self.bot.ban_cache.cache), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Boost Tier",
                        value=guild.premium_tier, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(
            name="Created", value=f"{format_dt(guild.created_at, style='F')} ({format_dt(guild.created_at, style='R')})", inline=True)

        await ctx.response.send_message(embed=embed)

    @app_commands.command()
    async def roleinfo(self, ctx: discord.Interaction, role: discord.Role) -> None:
        embed = discord.Embed(title="Role Statistics")
        embed.description = f"{len(role.members)} members have role {role.mention}"
        embed.color = role.color

        await ctx.respond(embed=embed)
