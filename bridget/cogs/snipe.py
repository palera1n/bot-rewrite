import discord

from typing import Any
from discord import app_commands
from discord.ext import commands

from utils import Cog
from utils.config import cfg
from utils.enums import PermissionLevel

class Snipe(Cog):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.cached_message = ""

    @commands.Cog.listener()
    async def on_message_edit(self, message: discord.Message, new_message: discord.Message) -> None:
        if message.author.bot:
            return

        self.cached_message = message
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        self.cached_message = message

    @commands.Cog.listener()
    async def on_automod_action(self, exectution: discord.AutoModAction) -> None:
        if isinstance(exectution.action.type, discord.AutoModRuleActionType.block_message):
            self.cached_message = message
    
    @PermissionLevel.MOD
    @app_commands.command()
    async def snipe(self, ctx: discord.Interaction) -> None:
        """Snipe a message

        Args:
            ctx (discord.Interaction): Context
        """
        
        if not self.cached_message:
            await ctx.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="No messages to snipe.",
                ),
            )
            return
        
        embed = discord.Embed(
            color=discord.Color.green(),
            description=self.cached_message.content,
        )
        embed.set_author(name=self.cached_message.author, icon_url=self.cached_message.author.avatar.url)
        embed.set_footer(text=f"Sent in #{self.cached_message.channel.name}")
        
        await ctx.response.send_message(embed=embed)
