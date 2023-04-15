import discord

from typing import Optional
from discord import app_commands

from utils import Cog, send_error, send_success, Errors, cfg


class Say(Cog):
    @app_commands.command()
    async def say(self, interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel]) -> None:
        """Make the bot say something

        :param message: Message to send
        :param channel: Channel to send to
        """

        if interaction.user.id != cfg.owner_id:
            await send_error(interaction, error=Errors.NO_PERMISSION)
            return

        channel = channel or interaction.channel
        await channel.send(message)

        await send_success(interaction)
