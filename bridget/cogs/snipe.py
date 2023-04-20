import discord

from typing import Any, Dict
from discord import app_commands
from discord.ext import commands

from utils import Cog
from utils.enums import PermissionLevel


class Snipe(Cog):
    cached_messages: Dict[discord.Message]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.cached_messages: Dict[discord.Message] = {}

    @commands.Cog.listener()
    async def on_message_edit(self, message: discord.Message, new_message: discord.Message) -> None:
        if message.author.bot:
            return

        self.cached_messages[message.channel.id] = message

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        self.cached_messages[message.channel.id] = message

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction) -> None:
        if isinstance(execution.action.type,
                      discord.AutoModRuleActionType.block_message):
            self.cached_messages[execution.channel_id] = execution.message

    @PermissionLevel.MOD
    @app_commands.command()
    async def snipe(self, ctx: discord.Interaction) -> None:
        """Snipe a message

        Args:
            ctx (discord.Interaction): Context
        """
        try:
            if not self.cached_messages[ctx.channel_id]:
                await ctx.response.send_message(
                    embed=discord.Embed(
                        color=discord.Color.red(),
                        description="No messages to snipe.",
                    ),
                )
                return
        except KeyError:
            await ctx.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="No messages to snipe.",
                ),
            )
            return

        embed = discord.Embed(
            color=discord.Color.green(),
            description=self.cached_messages[ctx.channel_id].content,
            timestamp=self.cached_messages[ctx.channel_id].created_at,
        )
        embed.set_author(
            name=self.cached_messages[ctx.channel_id].author,
            icon_url=self.cached_messages[ctx.channel_id].author.avatar.url)
        embed.set_footer(text=f"Sent in #{self.cached_messages[ctx.channel_id].channel.name}")
        
        try:
            if self.cached_messages[ctx.channel_id].attachments[0].type.startswith("image"):
                embed.set_image(url=self.cached_messages[ctx.channel_id].attachments[0].url)
        except:
            pass

        embed.set_thumbnail(url=self.cached_messages[ctx.channel_id].author.avatar.url)

        await ctx.response.send_message(embed=embed)
