import discord
import asyncio

from discord.ext import commands
from typing import Optional

from _typeshed import Incomplete
class Cog(commands.Cog):
    bot: Incomplete
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


async def send_error(ctx: discord.Interaction, description: str, embed: discord.Embed = None, delete_after: int = None) -> None:
    try:
        if embed:
            await ctx.response.send_message(
                embed=embed,
                ephemeral=True,
                delete_after=delete_after
            )
        else:
            await ctx.response.send_message(
                embed=discord.Embed(
                    title="An error occurred",
                    color=discord.Color.red(),
                    description=description,
                ),
                ephemeral=True,
                delete_after=delete_after
            )
    except discord.errors.InteractionResponded:
        if embed:
            followup = await ctx.followup.send(
                embed=embed,
                ephemeral=True
            )
        else:
            followup = await ctx.followup.send(
                embed=discord.Embed(
                    title="An error occurred",
                    color=discord.Color.red(),
                    description=description,
                ),
                ephemeral=True
            )

        if delete_after:
            await asyncio.sleep(delete_after)
            await followup.delete()


async def send_success(ctx: discord.Interaction, description: str = "Done!", embed: Optional[discord.Embed] = None, delete_after: Optional[int] = None, ephemeral: bool = True) -> None:
    if embed:
        await ctx.response.send_message(
            embed=embed,
            ephemeral=ephemeral,
            delete_after=delete_after
        )
    else:
        await ctx.response.send_message(
            embed=discord.Embed(
                color=discord.Color.green(),
                description=description,
            ),
            ephemeral=ephemeral,
            delete_after=delete_after
        )


async def reply_success(message: discord.Message, description: str = "Done!", embed: Optional[discord.Embed] = None, delete_after: Optional[int] = None) -> None:
    if embed:
        await message.reply(
            embed=embed,
            delete_after=delete_after
        )
    else:
        await message.reply(
            embed=discord.Embed(
                color=discord.Color.green(),
                description=description,
            ),
            delete_after=delete_after
        )


def format_number(number: int) -> str:
    return f"{number:,}"
