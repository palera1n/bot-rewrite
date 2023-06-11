import discord

from typing import Optional
from discord import app_commands

from utils import Cog, send_success
from utils.enums import PermissionLevel


class Say(Cog):
    @PermissionLevel.MOD
    @app_commands.command()
    async def say(self, ctx: discord.Interaction, message: str, channel: discord.TextChannel = None) -> None:
        """Make the bot say something

        :param message: Message to send
        :param channel: Channel to send to
        """

        channel = channel or ctx.channel
        await channel.send(message)

        await send_success(ctx)
