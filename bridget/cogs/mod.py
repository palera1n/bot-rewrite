import discord

from os import getenv
from typing import Optional
from discord import app_commands

from utils import Cog, send_error, send_success, Errors
from utils.mod import warn


class Mod(Cog):
    @app_commands.command()
    async def warn(self, interaction: discord.Interaction, user: discord.User, points: app_commands.Range[int, 1, 10], reason: str):
        """Warn a user

        Args:
            interaction (discord.Interaction): Interaction
            user (discord.User): User to warn
            points (app_commands.Range[int, 1, 10]): Points to give
            reason (str): Reason to warn
        """
        
        await interaction.response.defer()
        await warn(interaction, target_member=user, mod=interaction.author, points=points, reason=reason)
