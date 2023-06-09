import asyncio
import discord

from discord.ext import commands

from utils import Cog
from utils.config import cfg


class Sync(Cog):
    @commands.command()
    async def sync(self, ctx: commands.Context) -> None:
        """Sync slash commands"""

        if ctx.author.id != cfg.owner_id:
            await ctx.reply(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="You are not allowed to use this command.",
                ),
            )
            return

        async with ctx.typing():
            await self.bot.tree.sync(guild=discord.Object(id=cfg.guild_id))
            await self.bot.tree.sync()

        await ctx.reply(
            embed=discord.Embed(
                color=discord.Color.green(),
                description="Synced slash commands.",
            ),
            delete_after=5,
        )

        await asyncio.sleep(5)
        await ctx.message.delete()
