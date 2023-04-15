import discord

from os import getenv
from typing import Optional
from discord import app_commands

from ..utils import Cog, send_error, send_success, Errors

class Mod(Cog):
    async def warn(self, interaction: discord.Interaction, user: ModsAndAboveMemberOrUser, points: app_commands.Range[int, 1, 600], reason: str):
        if points < 1:  # can't warn for negative/0 points
            await send_error(interaction, error=Errors.POINTS_UNDER_ZERO)
            return

        await interaction.response.defer()
        await warn(ctx, target_member=user, mod=ctx.author, points=points, reason=reason)