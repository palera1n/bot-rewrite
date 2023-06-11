import discord
import random

from discord import ChannelType, app_commands
from datetime import datetime

from utils import Cog, send_error, send_success
from utils.modals import PostEmbedModal
from utils.services import guild_service
from utils.enums import PermissionLevel


class Helper(Cog):
    @app_commands.command()
    async def solved(self, ctx: discord.Interaction) -> None:
        """Close a support thread, usable by OP and Helpers

        Args:
            ctx (discord.ctx): Context
        """

        # error if channel is not a support thread
        if (ctx.channel.type != ChannelType.public_thread
            or ctx.channel.parent.type != ChannelType.forum
            or ctx.channel.parent_id != guild_service.get_guild().channel_support
        ):
            await send_error(ctx, "You can't mark this channel as solved")
            return

        # only OP and helpers can mark as solved
        if ctx.channel.owner_id != ctx.user.id:
            if not self == ctx.user:
                raise discord.app_commands.MissingPermissions(
                    "You don't have permission to use this command.")

        await send_success(ctx, "Thread marked as solved!", ephemeral=False)

        # fetch members and remove them from thread
        members = await ctx.channel.fetch_members()
        for member in members:
            await ctx.channel.remove_user(member)

        # lock and archive thread
        await ctx.channel.edit(archived=True, locked=True, reason=f"Thread marked as solved by {str(ctx.user)}")

    @PermissionLevel.HELPER
    @app_commands.command()
    async def postembed(self, ctx: discord.Interaction, title: str, channel: discord.TextChannel = None, image: discord.Attachment = None, color: str = None, anonymous: bool = False) -> None:
        """Sends an embed

        Args:
            ctx (discord.ctx): Context
            title (str): Title of the embed
            channel (discord.TextChannel): Channel to post the embed in
            color (str): Color of the embed in hexadecimal notation
            image (discord.Attachment): Image to show in embed
            anonymous (bool): Wether to show "Posted by" in footer
        """

        # TODO this can fail when parsing the hex color and will spit out
        # a full Python error to the user

        # if channel is not specified, default to the channel where
        # the interaction was ran in
        if channel is None:
            channel = ctx.channel

        # check if the user has permission to send to that channel
        perms = channel.permissions_for(ctx.user)
        if not perms.send_messages:
            await send_error(ctx, "You can't send messages in that channel!", delete_after=1)
            return

        # create the embed, add the image and color if specified
        embed = discord.Embed(title=title, timestamp=datetime.now())
        embed.set_footer(text="" if anonymous else f"Posted by {ctx.user.name}#{ctx.user.discriminator}")
        if image is not None:
            embed.set_image(url=image.url)
        if color is not None:
            # remove leading # sign
            if color.startswith('#'):
                color = color[1:]
            # shorthand notation (#faf)
            if len(color) == 3:
                color = color[0] * 2 + color[1] * 2 + color[2] * 2
            embed.color = int(color, 16)

        modal = PostEmbedModal(bot=self.bot, channel=channel, author=ctx.user)
        await ctx.response.send_modal(modal)
        await modal.wait()
        embed.description = modal.description

        # send the embed
        await channel.send(embed=embed)

    @PermissionLevel.HELPER
    @app_commands.command()
    async def poll(self, ctx: discord.Interaction, question: str, channel: discord.TextChannel = None, image: discord.Attachment = None, color: str = None) -> None:
        """Start a poll

        Args:
            ctx (discord.ctx): Context
            question (str): Question to ask
            channel (discord.TextChannel): Cchannel to post the poll in
            color (str): Color of the poll in hexadecimal notation
            image (discord.Attachment): Image to attach to poll
        """

        # TODO this can fail when parsing the hex color and will spit out
        # a full Python error to the user

        # if channel is not specified, default to the channel where
        # the interaction was ran in
        if channel is None:
            channel = ctx.channel

        # check if the user has permission to send to that channel
        perms = channel.permissions_for(ctx.user)
        if not perms.send_messages:
            await send_error(ctx, "You can't send messages in that channel!", delete_after=1)
            return

        # create the embed, add the image and color if specified
        embed = discord.Embed(
            description=question, color=random.randint(
                0, 16777215), timestamp=datetime.now())
        embed.set_footer(
            text=f"Poll started by {ctx.user.name}#{ctx.user.discriminator}")
        if image is not None:
            embed.set_image(url=image.url)
        if color is not None:
            # remove leading # sign
            if color.startswith('#'):
                color = color[1:]
            # shorthand notation (#faf)
            if len(color) == 3:
                color = color[0] * 2 + color[1] * 2 + color[2] * 2
            embed.color = int(color, 16)

        # send the embed
        msg = await channel.send(embed=embed)
        await msg.add_reaction('⬆️')
        await msg.add_reaction('⬇️')
        await send_success(ctx, "Poll started!", delete_after=1)

    @solved.error
    @postembed.error
    @poll.error
    async def error_handle(self, ctx: discord.Interaction, error: Exception) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await send_error(ctx, "You are not allowed to use this command.")
            return
