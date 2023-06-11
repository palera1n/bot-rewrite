import discord
import asyncio

from binascii import crc32
from datetime import datetime
from discord.ext import commands
from typing import List, Optional, Union
from discord import Color

class Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def hash_color(content: str) -> Color:
    # ChatGPT made this lmao
    color = crc32(content.encode('utf-8')) & 0xFFFFFF  # Get the lower 24 bits
    red = (color >> 16) & 0xFF
    green = (color >> 8) & 0xFF
    blue = color & 0xFF

    # Adjust the RGB components to create a pastel color
    red = int((red + 255) / 2)
    green = int((green + 255) / 2)
    blue = int((blue + 255) / 2)

    return Color.from_rgb(red, green, blue)


async def send_error(ctx: discord.Interaction, description: str, embed: discord.Embed = None, delete_after: int = None) -> None:
    try:
        if embed:
            await ctx.response.send_message(
                embed=embed,
                ephemeral=True,
                delete_after=delete_after
            )
        else:
            await ctx.response.send_message(
                embed=discord.Embed(
                    title="An error occurred",
                    color=discord.Color.red(),
                    description=description,
                ),
                ephemeral=True,
                delete_after=delete_after
            )
    except discord.errors.InteractionResponded:
        if embed:
            followup = await ctx.followup.send(
                embed=embed,
                ephemeral=True
            )
        else:
            followup = await ctx.followup.send(
                embed=discord.Embed(
                    title="An error occurred",
                    color=discord.Color.red(),
                    description=description,
                ),
                ephemeral=True
            )

        if delete_after:
            await asyncio.sleep(delete_after)
            await followup.delete()


async def send_success(ctx: discord.Interaction, description: str = "Done!", embed: Optional[discord.Embed] = None, delete_after: Optional[int] = None, ephemeral: bool = True) -> None:
    if embed:
        await ctx.response.send_message(
            embed=embed,
            ephemeral=ephemeral,
            delete_after=delete_after
        )
    else:
        await ctx.response.send_message(
            embed=discord.Embed(
                color=discord.Color.green(),
                description=description,
            ),
            ephemeral=ephemeral,
            delete_after=delete_after
        )


async def reply_success(message: discord.Message, description: str = "Done!", embed: Optional[discord.Embed] = None, delete_after: Optional[int] = None) -> None:
    if embed:
        await message.reply(
            embed=embed,
            delete_after=delete_after
        )
    else:
        await message.reply(
            embed=discord.Embed(
                color=discord.Color.green(),
                description=description,
            ),
            delete_after=delete_after
        )


def format_number(number: int) -> str:
    return f"{number:,}"


async def audit_logs_multi(guild: discord.Guild, actions: List[discord.AuditLogAction], limit: int, after: Union[discord.abc.Snowflake, datetime]) -> List[discord.AuditLogEntry]:
    logs = []
    for action in actions:
        logs.extend([audit async for audit in guild.audit_logs(limit=limit, action=action, after=after)])
    logs.sort(key=lambda x: x.created_at, reverse=True)
    return logs


pun_map = {
    "KICK": "Kicked",
    "BAN": "Banned",
    "CLEM": "Clemmed",
    "UNBAN": "Unbanned",
    "MUTE": "Duration",
    "REMOVEPOINTS": "Points removed"
}


def determine_emoji(type):
    emoji_dict = {
        "KICK": "👢",
        "BAN": "❌",
        "UNBAN": "✅",
        "MUTE": "🔇",
        "WARN": "⚠️",
        "UNMUTE": "🔈",
        "LIFTWARN": "⚠️",
        "REMOVEPOINTS": "⬇️",
        "CLEM": "👎"
    }
    return emoji_dict[type]

