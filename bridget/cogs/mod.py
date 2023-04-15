import discord

from os import getenv
from typing import Optional
from discord import app_commands

from utils import Cog, send_error, send_success, Errors
from utils.mod import warn


class Mod(Cog):
    @app_commands.command()
    async def warn(self, ctx: discord.Interaction, user: discord.Member, points: app_commands.Range[int, 1, 10], reason: str):
        """Warn a user

        Args:
            ctx (discord.ctx): Context
            user (discord.User): User to warn
            points (app_commands.Range[int, 1, 10]): Points to give
            reason (str): Reason to warn
        """
        
        await ctx.response.defer()
        # user = ctx.guild.get_member(interaction.user.id)
        await warn(ctx, target_member=user, mod=ctx.user, points=points, reason=reason)
