import asyncio
import discord

from typing import Optional
from discord import commands

from ..utils import Cog


class Sync(Cog):
    @commands.command()
    async def sync(self, ctx: commands.Context) -> None:
        """Sync slash commands"""
        if ctx.author.id != getenv("OWNER_ID"):
            await ctx.reply(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="You are not allowed to use this command.",
                ),
            )
            return

        await ctx.bot.tree.sync()

        await ctx.reply(
            embed=discord.Embed(
                color=discord.Color.green(),
                description="Synced slash commands.",
            ),
            delete_after=5,
        )
        
        await asyncio.sleep(5)
        await ctx.message.delete()
