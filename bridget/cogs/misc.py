import discord

from discord import app_commands

from utils import Cog, send_error, send_success
from utils.autocomplete import rule_autocomplete
from utils.services import guild_service


class Misc(Cog):
    @app_commands.autocomplete(title=rule_autocomplete)
    @app_commands.command()
    async def rule(self, ctx: discord.Interaction, title: str) -> None:
        """Posts a rule

        Args:
            ctx (discord.ctx): Context
            title (str): The title of the rule
        """

        try:
            channel = ctx.guild.get_channel(guild_service.get_guild().channel_rules)
            msg = await channel.fetch_message(int(title))

            await send_success(ctx, embed=msg.embeds[0], ephemeral=False)
        except:
            await send_error(ctx, "Could not find rule")


