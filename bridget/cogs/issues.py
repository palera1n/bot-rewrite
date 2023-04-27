import discord
import re
import asyncio

from io import BytesIO
from discord import Guild
from discord.ext import commands
from discord import app_commands
from discord.embeds import Embed

from model.issues import Issue
from utils import Cog, send_error, send_success
from utils.enums import PermissionLevel
from utils.modals import IssueModal, EditIssueModal
from utils.services import guild_service
from utils.autocomplete import issues_autocomplete

def prepare_issue_embed(issue: Issue) -> Embed:
    """Given an issue object, prepare the appropriate embed for it

    Parameters
    ----------
    issue : Issue
        Issue object from database

    Returns
    -------
    discord.Embed
        The embed we want to send
    """
    embed = discord.Embed(title=issue.name)
    embed.description = issue.content
    embed.timestamp = issue.added_date
    embed.color = discord.Color.blue()

    if issue.image.read() is not None:
        embed.set_image(url="attachment://image.gif" if issue.image.content_type ==
                        "image/gif" else "attachment://image.png")
    embed.set_footer(
        text=f"Submitted by {issue.added_by_tag}")
    return embed


def prepare_issue_view(issue: Issue) -> discord.ui.View:
    if not issue.button_links or issue.button_links is None:
        return discord.utils.MISSING

    view = discord.ui.View()
    for label, link in issue.button_links:
        # regex match emoji in label
        custom_emojis = re.search(
            r'<:\d+>|<:.+?:\d+>|<a:.+:\d+>|[\U00010000-\U0010ffff]', label)
        if custom_emojis is not None:
            emoji = custom_emojis.group(0).strip()
            label = label.replace(emoji, '')
            label = label.strip()
        else:
            emoji = None
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label=label,
                url=link,
                emoji=emoji))

    return view

async def refresh_common_issues(guild: Guild) -> None:
    # this function deletes the list message and
    # then resends the updated list.

    channel = guild.get_channel(guild_service.get_guild().channel_common_issues)

    # delete old list message
    if guild_service.get_guild().issues_list_msg is not None:
        for id in guild_service.get_guild().issues_list_msg:
            try: # if someone accidentally deletes something
                msg = await channel.fetch_message(id)
                await msg.delete()
            except:
                pass

    ids = []
    embed = Embed(title="Table of Contents")
    desc = ""
    page = 0

    for i, issue in enumerate(guild_service.get_guild().issues):
        desc += f"{i+1}. [{issue.name}](https://discord.com/channels/{guild.id}/{channel.id}/{issue.message_id})\n"
        if len(desc) > 3072:
            embed.description = desc
            page += 1
            embed.set_footer(text=f"Page {page}")
            msg = await channel.send(embed=embed)
            embed = Embed(title="")
            desc = ""
            ids.append(msg.id)

    if len(desc) > 0:
        embed.description = desc
        page += 1
        embed.set_footer(text=f"Page {page}")
        msg = await channel.send(embed=embed)
        ids.append(msg.id)

    guild_service.edit_issues_list(ids)

async def do_reindex(ctx: discord.Interaction) -> None:
    channel = ctx.guild.get_channel(guild_service.get_guild().channel_common_issues)

    for issue in guild_service.get_guild().issues:
        try:
            msg = await channel.fetch_message(issue.message_id)
            await msg.delete()
        except:
            pass

        _file = issue.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if issue.image.content_type == "image/gif" else "image.png")
        else:
            _file = discord.utils.MISSING

        msg = await channel.send(file=_file or discord.utils.MISSING, embed=prepare_issue_embed(issue) or discord.utils.MISSING, view=prepare_issue_view(issue) or discord.utils.MISSING)
        issue.message_id = msg.id

        guild_service.edit_issue(issue)

    # refresh common issue list
    await refresh_common_issues(ctx.guild)
    await ctx.followup.send(content="Reindexed!", ephemeral=True)


class Issues(Cog):
    @app_commands.autocomplete(name=issues_autocomplete)
    @app_commands.command()
    async def issue(self, ctx: discord.Interaction, name: str, user_to_mention: discord.Member = None) -> None:
        """Send a common issue

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the issue
            user_to_mention (discord.Member, optional): User to mention. Defaults to None.
        """

        name = name.lower()
        issue = guild_service.get_issue(name)

        if issue is None:
            raise commands.BadArgument("That issue does not exist.")

        # run cooldown so tag can't be spammed
        # bucket = self.tag_cooldown.get_bucket(tag.name)
        # current = datetime.now().timestamp()
        # ratelimit only if the invoker is not a moderator
        # if bucket.update_rate_limit(current) and not (gatekeeper.has(ctx.guild, ctx.user, 5) or ctx.guild.get_role(guild_service.get_guild().role_sub_mod) in ctx.user.roles):
        #    raise commands.BadArgument("That tag is on cooldown.")

        # if the Issue has an image, add it to the embed
        _file = issue.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if issue.image.content_type == "image/gif" else "image.png")
        else:
            _file = discord.utils.MISSING

        if user_to_mention is not None:
            title = f"Hey {user_to_mention.mention}, have a look at this!"
        else:
            title = None

        await ctx.response.send_message(content=title, embed=prepare_issue_embed(issue), view=prepare_issue_view(issue), file=_file)


class IssuesGroup(Cog, commands.GroupCog, group_name="commonissue"):
    @PermissionLevel.HELPER
    @app_commands.command()
    async def add(self, ctx: discord.Interaction, name: str, image: discord.Attachment = None) -> None:
        """Add a common issue

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the issue
            image (discord.Attachment, optional): Issue image. Defaults to None.
        """

        if (guild_service.get_issue(name)) is not None:
            raise commands.BadArgument("Issue with that name already exists.")

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

        modal = IssueModal(bot=self.bot, issue_name=name, author=ctx.user)
        await ctx.response.send_modal(modal)
        await modal.wait()

        issue = modal.issue
        if issue is None:
            return

        # did the user want to attach an image to this issue?
        if image is not None:
            issue.image.put(image, content_type=content_type)

        _file = issue.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if issue.image.content_type == "image/gif" else "image.png")


        # send the issue in #common-issues channel
        ci_channel = guild_service.get_guild().channel_common_issues
        ci_msg = await ctx.guild.get_channel(ci_channel).send(file=_file or discord.utils.MISSING, embed=prepare_issue_embed(issue) or discord.utils.MISSING, view=prepare_issue_view(issue) or discord.utils.MISSING)
        issue.message_id = ci_msg.id

        # store issue in database
        guild_service.add_issue(issue)

        # refresh common issue list
        await refresh_common_issues(ctx.guild)

        followup = await ctx.followup.send("Added new issue!", file=_file or discord.utils.MISSING, embed=prepare_issue_embed(issue) or discord.utils.MISSING, view=prepare_issue_view(issue) or discord.utils.MISSING)
        await asyncio.sleep(5)
        await followup.delete()

    @PermissionLevel.HELPER
    @app_commands.autocomplete(name=issues_autocomplete)
    @app_commands.command()
    async def edit(self, ctx: discord.Interaction, name: str, image: discord.Attachment = None) -> None:
        """Edit a common issue

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the issue
            image (discord.Attachment, optional): Issue image. Defaults to None.
        """


        issue = guild_service.get_issue(name)
        if issue is None:
            raise commands.BadArgument("That issue does not exist.")

        content_type = None
        if image is not None:
            # ensure the attached file is an image
            content_type = image.content_type
            if image.size > 8_000_000:
                raise commands.BadArgument("That image is too big!")

            image = await image.read()
            # save image bytes
            if issue.image is not None:
                issue.image.replace(image, content_type=content_type)
            else:
                issue.image.put(image, content_type=content_type)
        else:
            issue.image.delete()

        modal = EditIssueModal(issue=issue, author=ctx.user)
        await ctx.response.send_modal(modal)
        await modal.wait()

        if not modal.edited:
            await send_error(ctx, "Issue edit was cancelled.", ephemeral=True)
            return

        issue = modal.issue

        _file = issue.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if issue.image.content_type == "image/gif" else "image.png")

        # store issue in database
        guild_service.edit_issue(issue)

        # update the issue in #common-issues channel
        ci_channel = guild_service.get_guild().channel_common_issues
        ci_msg = await ctx.guild.get_channel(ci_channel).fetch_message(issue.message_id)
        await ci_msg.edit(attachments=[_file] if _file else [], embed=prepare_issue_embed(issue) or discord.utils.MISSING, view=prepare_issue_view(issue) or discord.utils.MISSING)

        followup = await ctx.followup.send("Edited issue!", file=_file or discord.utils.MISSING, embed=prepare_issue_embed(issue), view=prepare_issue_view(issue) or discord.utils.MISSING)
        await asyncio.sleep(5)
        await followup.delete()

    @PermissionLevel.HELPER
    @app_commands.autocomplete(name=issues_autocomplete)
    @app_commands.command()
    async def delete(self, ctx: discord.Interaction, name: str) -> None:
        """Delete a common issue

        Args:
            ctx (discord.Interaction): Context
            name (str): Name of the issue
        """

        issue = guild_service.get_issue(name)
        if issue is None:
            raise commands.BadArgument("That issue does not exist.")

        if issue.image is not None:
            issue.image.delete()

        # remove the issue in #common-issues channel
        ci_channel = guild_service.get_guild().channel_common_issues
        ci_msg = await ctx.guild.get_channel(ci_channel).fetch_message(issue.message_id)
        await ci_msg.delete()

        # delete the issue from the database
        guild_service.remove_issue(name)

        # refresh common issue list
        await refresh_common_issues(ctx.guild)

        await send_success(ctx, f"Deleted issue `{issue.name}`.", delete_after=5)

    @PermissionLevel.HELPER
    @app_commands.command()
    async def reindex(self, ctx: discord.Interaction) -> None:
        """Reposts the issues in the common issues channel

        Args:
            ctx (discord.Interaction): Context
        """

        await ctx.response.defer(ephemeral=True, thinking=True)
        ctx.client.loop.create_task(do_reindex(ctx))
