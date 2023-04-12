import discord
from discord.ext import commands
import os
from utils.checks.check_invokee import check_invokee
from model import Case, Cases
from utils.command_groups import modactions_group


class WarnCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        print("Warn cog is ready")

    # TODO: rewrite warn cog

    #@modactions_group.slash_command(name="warn", description="Warn a user")
    

#    @warn.error
#    @removewarn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have the required permissions to \
                    use this command.", ephemeral=True)


def setup(bot):
    bot.add_cog(WarnCog(bot))
