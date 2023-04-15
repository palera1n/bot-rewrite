import discord

from os import getenv
from typing import Optional
from discord import app_commands

from utils import Cog, send_error, send_success, Errors
from utils.mod import warn


class Mod(Cog):
    @app_commands.command()
    async def warn(self, interaction: discord.Interaction, user: discord.User, reason: str):
        await interaction.response.defer()
        await warn(interaction, target_member=user, mod=interaction.author, points=1, reason=reason)
