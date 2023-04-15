import discord

from discord.ext import commands

from .enums import Errors

class Cog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: dict):
        self.bot = bot
        self.config = config

async def send_error(interaction: discord.Interaction, error: Errors = Errors.NO_PERMISSION) -> None:
    match error:
        case Errors.NO_PERMISSION:
            description = "You are not allowed to use this command."
        case Errors.POINTS_UNDER_ZERO:
            description = "Points can't be lower than 1."
    
    await interaction.response.send_message(
        embed=discord.Embed(
            color=discord.Color.red(),
            description=description,
        ),
        ephemeral=True,
    )

async def send_success(interaction: discord.Interaction, description: str = "Done!") -> None:
    await interaction.response.send_message(
        embed=discord.Embed(
            color=discord.Color.green(),
            description=description,
        ),
        ephemeral=True,
    )
