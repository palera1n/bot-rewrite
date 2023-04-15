import discord

from os import getenv
from typing import Optional
from discord import commands

from utils import Cog, send_error, send_success, Errors
from utils.mod import warn

class Mod(Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command()
    async def warn(self, ctx: discord.Interaction, user: discord.User, reason: str):
        await ctx.response.defer()
        await warn(ctx, target_member=user, mod=ctx.author, points=1, reason=reason)

def setup(bot):
    bot.add_cog(Mod(bot))