import discord

from typing import Optional
from discord import app_commands

from utils import Cog, send_error, send_success, cfg


class Say(Cog):
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command()
    async def say(self, ctx: discord.Interaction, message: str, channel: Optional[discord.TextChannel]) -> None:
        """Make the bot say something

        :param message: Message to send
        :param channel: Channel to send to
        """

        if ctx.user.id != cfg.owner_id:
            await send_error(ctx, "You are not allowed to use this command.")
            return

        channel = channel or ctx.channel
        await channel.send(message)

        await send_success(ctx)
