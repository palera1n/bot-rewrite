import discord
import asyncio
import humanize

from typing import Optional, List, Union
from discord.utils import escape_markdown
from discord.embeds import Embed
from discord.interactions import Interaction
from datetime import timezone

from model import *
from utils.config import cfg
from utils.services import guild_service, user_service
from model.guild import Guild


async def add_unban_infraction(target_member: discord.Member, mod: discord.Member, reason: str, db_guild: Guild, bot: discord.Client) -> Embed:
    infraction = Infraction(
        _id=db_guild.infraction_id,
        _type="UNBAN",
        mod_id=mod.id,
        mod_tag=str(mod),
        reason=reason,
    )
    guild_service.inc_infractionid()
    user_service.add_infraction(target_member.id, infraction)
    log = prepare_unban_log(mod, target_member, infraction)
    await notify_user(target_member, f"You have been unbanned in {bot.get_guild(guild_service.get_guild()._id).name}", log)
    return create_public_log(db_guild, target_member, log)


async def add_mute_infraction(target_member: discord.Member, mod: discord.Member, reason: str, db_guild: Guild, bot: discord.Client) -> Embed:
    now = datetime.now(tz=timezone.utc)

    
    infraction = Infraction(
        _id=db_guild.infraction_id,
        _type="MUTE",
        mod_id=mod.id,
        mod_tag=str(mod),
        punishment=humanize.naturaldelta(
            target_member.timed_out_until - now, minimum_unit="seconds"),
        reason=reason,
    )
    guild_service.inc_infractionid()
    user_service.add_infraction(target_member.id, infraction)
    log = prepare_mute_log(mod, target_member, infraction)
    await notify_user(target_member, f"You have been muted in {bot.get_guild(guild_service.get_guild()._id).name}", log)
    return create_public_log(db_guild, target_member, log)


async def add_unmute_infraction(target_member: discord.Member, mod: discord.Member, reason: str, db_guild: Guild, bot: discord.Client) -> Embed:
    infraction = Infraction(
        _id=db_guild.infraction_id,
        _type="UNMUTE",
        mod_id=mod.id,
        mod_tag=str(mod),
        reason=reason,
    )
    guild_service.inc_infractionid()
    user_service.add_infraction(target_member.id, infraction)
    log = prepare_unmute_log(mod, target_member, infraction)
    await notify_user(target_member, f"You have been unmuted in {bot.get_guild(guild_service.get_guild()._id).name}", log)
    return create_public_log(db_guild, target_member, log)


async def add_kick_infraction(target_member: discord.Member, mod: discord.Member, reason: str, db_guild: Guild, bot: discord.Client) -> Embed:
    """Adds kick infraction to user

    Args:
        target_member (discord.Member): User who was kicked
        mod (discord.Member): User that kicked
        reason (str): Reason user was kicked
        db_guild (_type_): Guild DB

    Returns:
        _type_: _description_
    """

    infraction = Infraction(
        _id=db_guild.infraction_id,
        _type="KICK",
        mod_id=mod.id,
        mod_tag=str(mod),
        reason=reason,
    )

    guild_service.inc_infractionid()
    user_service.add_infraction(target_member.id, infraction)
    log = prepare_kick_log(mod, target_member, infraction)
    await notify_user(target_member, f"You have been kicked in {bot.get_guild(guild_service.get_guild()._id).name}", log)

    return create_public_log(db_guild, target_member, log)


async def warn(ctx: discord.Interaction, target_member: discord.Member, mod: discord.Member, points: int, reason: str, no_interaction: bool = False) -> None:
    db_guild = guild_service.get_guild()

    infraction = Infraction(
        _id=db_guild.infraction_id,
        _type="WARN",
        mod_id=mod.id,
        mod_tag=str(mod),
        reason=escape_markdown(reason),
        punishment=str(points)
    )

    guild_service.inc_infractionid()
    user_service.add_infraction(target_member.id, infraction)
    user_service.inc_points(target_member.id, points)

    db_user = user_service.get_user(target_member.id)
    cur_points = db_user.warn_points

    log = prepare_warn_log(mod, target_member, infraction)
    log.add_field(name="Current points", value=f"{cur_points}/10", inline=True)

    dmed = await notify_user_warn(ctx, target_member, mod, db_user, db_guild, cur_points, log)
    await response_log(ctx, log, no_interaction=no_interaction)
    await submit_public_log(ctx, db_guild, target_member, log, dmed)


async def notify_user(target_member: discord.Member, text: str, log: discord.Embed) -> bool:
    """Notifies a specified user about something

    Args:
        target_member (discord.Member): User to notify
        text (str): Text to send
        log (discord.Embed): Embed to send

    Returns:
        bool: If notify succeeded
    """

    try:
        await target_member.send(text, embed=log)
    except Exception:
        return False

    return True


async def notify_user_warn(ctx: discord.Interaction, target_member: discord.Member, mod: discord.Member, db_user, db_guild: Guild, cur_points: int, log) -> bool:
    """Notifies a specified user about a warn

    Args:
        ctx (discord.Interaction): Context
        target_member (discord.Member): User to notify
        mod (discord.Member): User that warned
        db_user (_type_): User DB
        db_guild (_type_): Guild DB
        cur_points (int): Number of points the user currently has
        log (_type_): Embed to send

    Returns:
        bool: If notify succeeded
    """

    log_kickban = None
    dmed = True

    if cur_points >= 10:
        # if cfg.ban_appeal_url is None:
        dmed = await notify_user(target_member, f"You were banned from {ctx.guild.name} for reaching 10 or more points.", log)
        # else:
        # dmed = await notify_user(target_member, f"You were banned from
        # {ctx.guild.name} for reaching 10 or more points.\n\nIf you would like
        # to appeal your ban, please fill out this form:
        # <{cfg.ban_appeal_url}>", log)

        log_kickban = await add_ban_infraction(target_member, mod, "10 or more warn points reached.", db_guild, ctx.client)
        await target_member.ban(reason="10 or more warn points reached.")
    elif cur_points >= 8 and not db_user.was_warn_kicked and isinstance(target_member, discord.Member):
        # kick user if >= 8 points and wasn't previously kicked
        user_service.set_warn_kicked(target_member.id)

        dmed = await notify_user(target_member, f"You were kicked from {ctx.guild.name} for reaching 8 or more points. Please note that you will be banned at 10 points.", log)
        log_kickban = add_kick_infraction(
            target_member,
            mod,
            "8 or more warn points reached.",
            db_guild, bot=ctx.client)
        await target_member.kick(reason="8 or more warn points reached.")
    else:
        if isinstance(target_member, discord.Member):
            dmed = await notify_user(target_member, f"You were warned in {ctx.guild.name}. Please note that you will be kicked at 8 points and banned at 10 points.", log)

    if log_kickban:
        await submit_public_log(ctx, db_guild, target_member, log_kickban)

    return dmed


async def response_log(ctx: Interaction, log, no_interaction: bool = False) -> None:
    if no_interaction:
        await ctx.channel.send(embed=log, delete_after=10)
        return

    if isinstance(ctx, discord.Interaction):
        if ctx.response.is_done():
            res = await ctx.followup.send(embed=log)
            await res.delete(delay=10)
        else:
            await ctx.response.send_message(embed=log)
            ctx.client.loop.create_task(delay_delete(ctx))
    else:
        await ctx.send(embed=log, delete_after=10)


def create_public_log(db_guild: Guild,
                      user: Union[discord.Member,
                                  discord.User],
                      log: discord.Embed) -> Embed:
    """Submits a public log

    Args:
        ctx (discord.Interaction): Context
        db_guild (Guild): Guild DB
        user (Union[discord.Member, discord.User]): User to notify
        log (discord.Embed): Embed to send
        dmed (bool, optional): If was dmed. Defaults to None.
    """

    log.remove_author()
    log.set_thumbnail(url=user.display_avatar)
    #log.remove_field(1)
    return log


async def submit_public_log(ctx: discord.Interaction, db_guild: Guild, user: Union[discord.Member, discord.User], log: discord.Embed, dmed: bool = None) -> None:
    """Submits a public log

    Args:
        ctx (discord.Interaction): Context
        db_guild (Guild): Guild DB
        user (Union[discord.Member, discord.User]): User to notify
        log (discord.Embed): Embed to send
        dmed (bool, optional): If was dmed. Defaults to None.
    """

    public_channel = ctx.guild.get_channel(db_guild.channel_public)
    if public_channel:
        log.remove_author()
        log.set_thumbnail(url=user.display_avatar)
        log.remove_field(1)
        if dmed is not None:
            await public_channel.send(user.mention if not dmed else "", embed=log)
        else:
            await public_channel.send(embed=log)


async def add_ban_infraction(target_member: discord.Member, mod: discord.Member, reason, db_guild: Guild, bot: discord.Client) -> Embed:
    """_summary_

    Args:
        target_member (discord.Member): User who was banned
        mod (discord.Member): User who banned
        reason (_type_): Reason user was banned
        db_guild (Guild, optional): Guild DB. Defaults to None.

    Returns:
        _type_: _description_
    """

    infraction = Infraction(
        _id=db_guild.infraction_id,
        _type="BAN",
        mod_id=mod.id,
        mod_tag=str(mod),
        punishment="PERMANENT",
        reason=reason,
    )

    guild_service.inc_infractionid()
    user_service.add_infraction(target_member.id, infraction)
    log = prepare_ban_log(mod, target_member, infraction)
    await notify_user(target_member, f"You have been banned in {bot.get_guild(guild_service.get_guild()._id).name}", log)

    return create_public_log(db_guild, target_member, log)


async def delay_delete(interaction: discord.Interaction) -> None:
    await asyncio.sleep(10)
    await interaction.delete_original_message()

# TODO: Fix all of this


def prepare_warn_log(mod, target_member, infraction) -> Embed:
    """Prepares warn log

    Parameters
    ----------
    mod : discord.Member
        "Mod who warned the member"
    target_member : discord.Member
        "Member who was warned"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Warned")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.orange()
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Increase", value=infraction.punishment, inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_liftwarn_log(mod, target_member, infraction) -> Embed:
    """Prepares liftwarn log

    Parameters
    ----------
    mod : discord.Member
        "Mod who lifted the warn"
    target_member : discord.Member
        "Member who's warn was lifted"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Warn Lifted")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.blurple()
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Decrease", value=infraction.punishment, inline=True)
    embed.add_field(name="Reason", value=infraction.lifted_reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.lifted_date
    return embed


def prepare_editreason_log(mod, target_member, infraction, old_reason) -> Embed:
    """Prepares log for reason edits

    Parameters
    ----------
    mod : discord.Member
        "Mod who updated the reason"
    target_member : discord.Member
        "Member who's infraction reason was edited"
    infraction
        "Infraction object"
    old_reason : str
        "Old infraction reason"

    """
    embed = discord.Embed(title="Member Infraction Updated")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.blurple()
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Old reason", value=old_reason, inline=False)
    embed.add_field(name="New Reason", value=infraction.reason, inline=False)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_removepoints_log(mod, target_member, infraction) -> Embed:
    """Prepares log for point removal

    Parameters
    ----------
    mod : discord.Member
        "Mod who removed the points"
    target_member : discord.Member
        "Member whose points were removed"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Points Removed")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.blurple()
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Decrease", value=infraction.punishment, inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_ban_log(mod, target_member, infraction) -> Embed:
    """Prepares ban log

    Parameters
    ----------
    mod : discord.Member
        "Mod who banned the member"
    target_member : discord.Member
        "Member who was banned"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Banned")
    embed.color = discord.Color.blue()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_unban_log(mod, target_member, infraction) -> Embed:
    """Prepares unban log

    Parameters
    ----------
    mod : discord.Member
        "Mod who unbanned the member"
    target_member : discord.Member
        "Member who was unbanned"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Unbanned")
    embed.color = discord.Color.blurple()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.id})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_kick_log(mod, target_member, infraction) -> Embed:
    """Prepares kick log

    Parameters
    ----------
    mod : discord.Member
        "Mod who kicked the member"
    target_member : discord.Member
        "Member who was kicked"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Kicked")
    embed.color = discord.Color.green()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=False)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_mute_log(mod, target_member, infraction) -> Embed:
    """Prepares mute log

    Parameters
    ----------
    mod : discord.Member
        "Mod who muted the member"
    target_member : discord.Member
        "Member who was muted"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Muted")
    embed.color = discord.Color.red()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Duration", value=infraction.punishment, inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed


def prepare_unmute_log(mod, target_member, infraction) -> Embed:
    """Prepares unmute log

    Parameters
    ----------
    mod : discord.Member
        "Mod who unmuted the member"
    target_member : discord.Member
        "Member who was unmuted"
    infraction
        "Infraction object"

    """
    embed = discord.Embed(title="Member Unmuted")
    embed.color = discord.Color.green()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(
        name="Member",
        value=f'{target_member} ({target_member.mention})',
        inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=infraction.reason, inline=True)
    embed.set_footer(text=f"Infraction #{infraction._id} | {target_member.id}")
    embed.timestamp = infraction.date
    return embed

