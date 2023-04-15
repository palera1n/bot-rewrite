import discord

from discord.ext import commands

class Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def send_error(ctx: discord.Interaction, message: str) -> None:
    await ctx.response.send_message(
        embed=discord.Embed(
            color=discord.Color.red(),
            description=message,
        ),
        ephemeral=True,
    )

async def send_success(ctx: discord.Interaction, description: str = "Done!", embed: discord.Embed = None, delete_after: int = None) -> None:
    if embed:
        await ctx.response.send_message(
            embed=embed,
            ephemeral=True,
            delete_after=delete_after
        )
    else:
        await ctx.response.send_message(
            embed=discord.Embed(
                color=discord.Color.green(),
                description=description,
            ),
            ephemeral=True,
            delete_after=delete_after
        )
