import discord
import asyncio

from binascii import crc32
from datetime import datetime
from discord.ext import commands
from typing import Any, List, Optional, Union
from discord import Color, app_commands

from model.user import User
from utils.autocomplete import transform_groups
from utils.fetchers import get_ios_cfw

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


def get_text_channel_by_name(guild: discord.Guild, name: str) -> Optional[discord.TextChannel]:
    for channel in guild.text_channels:
        if channel.name == name:
            return channel


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


async def send_success(ctx: discord.Interaction, description: str = "Done!", embed: discord.Embed = None, delete_after: int = None, ephemeral: bool = True) -> None:
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


async def reply_success(message: discord.Message, description: str = "Done!", embed: discord.Embed = None, delete_after: int = None) -> None:
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


def get_warnpoints(user: User) -> int:
    return 9 if user.is_clem else user.warn_points


pun_map = {
    "KICK": "Kicked",
    "BAN": "Banned",
    "CLEM": "Clemmed",
    "UNCLEM": "Unclemmed",
    "UNBAN": "Unbanned",
    "MUTE": "Duration",
    "REMOVEPOINTS": "Points removed"
}


def determine_emoji(type: str) -> str:
    emoji_dict = {
        "KICK": "👢",
        "BAN": "❌",
        "UNBAN": "✅",
        "MUTE": "🔇",
        "WARN": "⚠️",
        "UNMUTE": "🔈",
        "LIFTWARN": "⚠️",
        "REMOVEPOINTS": "⬇️",
        "CLEM": "👎",
        "UNCLEM": "👍"
    }
    return emoji_dict[type]

async def get_device(value: str) -> dict:
    response = await get_ios_cfw()
    device_groups = response.get("group")

    transformed_groups = transform_groups(device_groups)
    devices = [group for group in transformed_groups if group.get(
        'name').lower() == value.lower() or value.lower() in [x.lower() for x in group.get('devices')]]

    if not devices:
        raise app_commands.AppCommandError(
            "No device found with that name.")

    return devices[0]

async def get_version_on_device(version: str, device: dict) -> dict:
    response = await get_ios_cfw()
    board = device.get("devices")[0]

    ios = response.get("ios")

    # ios = [i for _, i in ios.items()]
    for os_version in ["iOS", "tvOS", "watchOS"]:
        version = version.replace(os_version + " ", "")
    firmware = [v for v in ios if board in v.get(
        'devices') and version == v.get('version') or version.lower() == v.get("uniqueBuild").lower()]
    if not firmware:
        raise app_commands.AppCommandError(
            "No firmware found with that version.")

    return firmware[0]


class InstantQueueTS:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()
        self.event = asyncio.Event()

    async def put(self, item: Any) -> None:
        async with self.lock:
            asyncio.get_event_loop().call_soon_threadsafe(self.queue.put_nowait, item)
            self.event._loop.call_soon_threadsafe(self.event.set)

    async def get(self) -> Any:
        await self.event.wait()
        self.event.clear()
        return self.queue.get_nowait()

    def task_done(self) -> None:
        self.queue.task_done()

