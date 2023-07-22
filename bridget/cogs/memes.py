import discord
import asyncio

from io import BytesIO
from discord import app_commands
from discord.ext import commands

from utils import Cog, send_error, send_success
from utils.enums import PermissionLevel
from utils.menus import Menu
from utils.modals import TagModal, EditTagModal
from utils.services import guild_service
from utils.autocomplete import memes_autocomplete
from cogs.tags import format_tag_page, prepare_tag_embed, prepare_tag_view


class Memes(Cog):
    @app_commands.autocomplete(name=memes_autocomplete)
    @app_commands.command()
    async def meme(self, ctx: discord.Interaction, name: str, user_to_mention: discord.Member = None) -> None:
        """Send a meme

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the meme
            user_to_mention (discord.Member, optional): User to mention. Defaults to None.
        """

        name = name.lower()
        tag = guild_service.get_meme(name)

        if tag is None:
            raise commands.BadArgument("That meme does not exist.")

        # run cooldown so tag can't be spammed
        # bucket = self.tag_cooldown.get_bucket(tag.name)
        # current = datetime.now().timestamp()
        # ratelimit only if the invoker is not a moderator
        # if bucket.update_rate_limit(current) and not (gatekeeper.has(ctx.guild, ctx.user, 5) or ctx.guild.get_role(guild_service.get_guild().role_sub_mod) in ctx.user.roles):
        #    raise commands.BadArgument("That tag is on cooldown.")

        # if the Tag has an image, add it to the embed
        _file = tag.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")
        else:
            _file = discord.utils.MISSING

        if user_to_mention is not None:
            title = f"Hey {user_to_mention.mention}, have a look at this!"
        else:
            title = None

        await ctx.response.send_message(content=title, embed=prepare_tag_embed(tag), view=prepare_tag_view(tag), file=_file)

    @commands.guild_only()
    @commands.command(name="meme", aliases=["m"])
    async def _tag(self, ctx: commands.Context, name: str) -> None:
        """Send a tag

        Args:
            ctx (commands.Context): Context
            name (str): Name of the tag
        """

        name = name.lower()
        tag = guild_service.get_tag(name)

        if tag is None:
            raise commands.BadArgument("That tag does not exist.")

        # if the Tag has an image, add it to the embed
        _file = tag.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")
        else:
            _file = discord.utils.MISSING

        if ctx.message.reference is not None:
            title = f"Hey {ctx.message.reference.resolved.author.mention}, have a look at this!"
            await ctx.send(content=title, embed=prepare_tag_embed(tag), view=prepare_tag_view(tag), file=_file)
        else:
            await ctx.message.reply(embed=prepare_tag_embed(tag), view=prepare_tag_view(tag), file=_file, mention_author=False)


    @app_commands.command()
    async def memelist(self, ctx: discord.Interaction) -> None:
        """List all memes

        Args:
            ctx (discord.Interaction): Context
        """

        _tags = sorted(
            guild_service.get_guild().memes,
            key=lambda tag: tag.name)

        if len(_tags) == 0:
            raise commands.BadArgument("There are no memes defined.")

        menu = Menu(
            ctx,
            _tags,
            per_page=12,
            page_formatter=format_tag_page,
            whisper=True)
        await menu.start()


class MemesGroup(Cog, commands.GroupCog, group_name="memes"):
    @PermissionLevel.HELPER
    @app_commands.command()
    async def add(self, ctx: discord.Interaction, name: str, image: discord.Attachment = None) -> None:
        """Add a meme

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the meme
            image (discord.Attachment, optional): Meme image. Defaults to None.
        """

        if not name.isalnum():
            raise commands.BadArgument("Meme name must be alphanumeric.")

        if len(name.split()) > 1:
            raise commands.BadArgument(
                "Meme names can't be longer than 1 word.")

        if (guild_service.get_tag(name.lower())) is not None:
            raise commands.BadArgument("Meme with that name already exists.")

        content_type = None
        if image is not None:
            content_type = image.content_type
            if content_type not in [
                "image/png",
                "image/jpeg",
                "image/gif",
                    "image/webp"]:
                raise commands.BadArgument("Attached file was not an image!")

            if image.size > 8_000_000:
                raise commands.BadArgument("That image is too big!")

            image = await image.read()

        modal = TagModal(bot=self.bot, tag_name=name, author=ctx.user)
        await ctx.response.send_modal(modal)
        await modal.wait()

        tag = modal.tag
        if tag is None:
            return

        # did the user want to attach an image to this tag?
        if image is not None:
            tag.image.put(image, content_type=content_type)

        # store tag in database
        guild_service.add_meme(tag)

        _file = tag.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")

        followup = await ctx.followup.send("Added new meme!", file=_file or discord.utils.MISSING, embed=prepare_tag_embed(tag) or discord.utils.MISSING, view=prepare_tag_view(tag) or discord.utils.MISSING)
        await asyncio.sleep(5)
        await followup.delete()

    @PermissionLevel.HELPER
    @app_commands.autocomplete(name=memes_autocomplete)
    @app_commands.command()
    async def edit(self, ctx: discord.Interaction, name: str, image: discord.Attachment = None) -> None:
        """Edit a meme

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the meme
            image (discord.Attachment, optional): Meme image. Defaults to None.
        """

        if len(name.split()) > 1:
            raise commands.BadArgument(
                "Meme names can't be longer than 1 word.")

        name = name.lower()
        tag = guild_service.get_meme(name)

        if tag is None:
            raise commands.BadArgument("That meme does not exist.")

        content_type = None
        if image is not None:
            # ensure the attached file is an image
            content_type = image.content_type
            if image.size > 8_000_000:
                raise commands.BadArgument("That image is too big!")

            image = await image.read()
            # save image bytes
            if tag.image is not None:
                tag.image.replace(image, content_type=content_type)
            else:
                tag.image.put(image, content_type=content_type)
        else:
            tag.image.delete()

        modal = EditTagModal(tag=tag, author=ctx.user)
        await ctx.response.send_modal(modal)
        await modal.wait()

        if not modal.edited:
            await send_error(ctx, "Meme edit was cancelled.", ephemeral=True)
            return

        tag = modal.tag

        # store tag in database
        guild_service.edit_meme(tag)

        _file = tag.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")

        followup = await ctx.followup.send("Edited meme!", file=_file or discord.utils.MISSING, embed=prepare_tag_embed(tag), view=prepare_tag_view(tag) or discord.utils.MISSING)
        await asyncio.sleep(5)
        await followup.delete()

    @PermissionLevel.HELPER
    @app_commands.autocomplete(name=memes_autocomplete)
    @app_commands.command()
    async def delete(self, ctx: discord.Interaction, name: str) -> None:
        """Delete a meme

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the meme
        """

        name = name.lower()

        tag = guild_service.get_meme(name)
        if tag is None:
            raise commands.BadArgument("That meme does not exist.")

        if tag.image is not None:
            tag.image.delete()

        guild_service.remove_meme(name)
        await send_success(ctx, f"Deleted meme `{tag.name}`.", delete_after=5)
