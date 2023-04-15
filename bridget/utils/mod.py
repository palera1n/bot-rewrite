import discord

from utils.services import guild_service, user_service

def add_kick_case(target_member: discord.Member, mod: discord.Member, reason: str, db_guild):
    """Adds kick case to user

    Args:
        target_member (discord.Member): User who was kicked
        mod (discord.Member): User that kicked
        reason (str): Reason user was kicked
        db_guild (_type_): Guild DB

    Returns:
        _type_: _description_
    """
    
    case = Case(
        _id=db_guild.case_id,
        _type="KICK",
        mod_id=mod.id,
        mod_tag=str(mod),
        reason=reason,
    )

    guild_service.inc_caseid()
    user_service.add_case(target_member.id, case)

    return prepare_kick_log(mod, target_member, case)

async def warn(interaction: discord.Interaction, target_member: discord.Member, mod: discord.Member, points, reason):
    db_guild = guild_service.get_guild()

    case = Case(
        _id=db_guild.case_id,
        _type="WARN",
        mod_id=mod.id,
        mod_tag=str(mod),
        reason=escape_markdown(reason),
        punishment=str(points)
    )

    guild_service.inc_caseid()
    user_service.add_case(target_member.id, case)
    user_service.inc_points(target_member.id, points)

    db_user = user_service.get_user(target_member.id)
    cur_points = db_user.warn_points

    # TODO: Implement logging
    # log = prepare_warn_log(mod, target_member, case)
    # log.add_field(name="Current points", value=cur_points, inline=True)

    dmed = await notify_user_warn(interaction, target_member, mod, db_user, db_guild, cur_points, log)
    await response_log(interaction, log)
    await submit_public_log(interaction, db_guild, target_member, log, dmed)

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

async def notify_user_warn(interaction: discord.Interaction, target_member: discord.Member, mod: discord.Member, db_user, db_guild, cur_points: int, log) -> bool:
    """Notifies a specified user about a warn

    Args:
        interaction (discord.Interaction): Interaction
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
        if cfg.ban_appeal_url is None:
            dmed = await notify_user(target_member, f"You were banned from {ctx.guild.name} for reaching 10 or more points.", log)
        else:
            dmed = await notify_user(target_member, f"You were banned from {ctx.guild.name} for reaching 10 or more points.\n\nIf you would like to appeal your ban, please fill out this form: <{cfg.ban_appeal_url}>", log)

        log_kickban = await add_ban_case(target_member, mod, "10 or more warn points reached.", db_guild)
        await target_member.ban(reason="10 or more warn points reached.")

        if isinstance(ctx, discord.Interaction):
            ctx.client.ban_cache.ban(target_member.id)
        else:
            ctx.bot.ban_cache.ban(target_member.id)

    elif cur_points >= 8 and not db_user.was_warn_kicked and isinstance(target_member, discord.Member):
        # kick user if >= 8 points and wasn't previously kicked
        user_service.set_warn_kicked(target_member.id)

        dmed = await notify_user(target_member, f"You were kicked from {ctx.guild.name} for reaching 8 or more points. Please note that you will be banned at 10 points.", log)
        log_kickban = add_kick_case(target_member, mod, "8 or more warn points reached.", db_guild)
        await target_member.kick(reason="8 or more warn points reached.")
    else:
        if isinstance(target_member, discord.Member):
            dmed = await notify_user(target_member, f"You were warned in {ctx.guild.name}. Please note that you will be kicked at 8 points and banned at 10 points.", log)

    if log_kickban:
        await submit_public_log(ctx, db_guild, target_member, log_kickban)

    return dmed

async def response_log(ctx, log):
    if isinstance(ctx, discord.Interaction):
        if ctx.response.is_done():
            res = await ctx.followup.send(embed=log)
            await res.delete(delay=10)
        else:
            await ctx.response.send_message(embed=log)
            ctx.client.loop.create_task(delay_delete(ctx))
    else:
        await ctx.send(embed=log, delete_after=10)


async def submit_public_log(interaction: discord.Interaction, db_guild: Guild, user: Union[discord.Member, discord.User], log: discord.Embed, dmed: bool = None):
    """Submits a public log

    Args:
        interaction (discord.Interaction): Interaction
        db_guild (Guild): Guild DB
        user (Union[discord.Member, discord.User]): User to notify
        log (discord.Embed): Embed to send
        dmed (bool, optional): If was dmed. Defaults to None.
    """
    
    public_channel = ctx.guild.get_channel(
        db_guild.channel_public)
    if public_channel:
        log.remove_author()
        log.set_thumbnail(url=user.display_avatar)
        if dmed is not None:
            await public_channel.send(user.mention if not dmed else "", embed=log)
        else:
            await public_channel.send(embed=log)


async def add_ban_case(target_member: discord.Member, mod: discord.Member, reason, db_guild: Guild = None):
    """_summary_

    Args:
        target_member (discord.Member): User who was banned
        mod (discord.Member): User who banned
        reason (_type_): Reason user was banned
        db_guild (Guild, optional): Guild DB. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    case = Case(
        _id=db_guild.case_id,
        _type="BAN",
        mod_id=mod.id,
        mod_tag=str(mod),
        punishment="PERMANENT",
        reason=reason,
    )

    guild_service.inc_caseid()
    user_service.add_case(target_member.id, case)
    return prepare_ban_log(mod, target_member, case)

async def delay_delete(interaction: discord.Interaction):
    await asyncio.sleep(10)
    await interaction.delete_original_message()

# TODO: Fix all of this
def prepare_warn_log(mod, target_member, case):
    """Prepares warn log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who warned the member"
    target_member : discord.Member
        "Member who was warned"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Warned")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.orange()
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Increase", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_liftwarn_log(mod, target_member, case):
    """Prepares liftwarn log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who lifted the warn"
    target_member : discord.Member
        "Member who's warn was lifted"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Warn Lifted")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.blurple()
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Decrease", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.lifted_reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.lifted_date
    return embed

def prepare_editreason_log(mod, target_member, case, old_reason):
    """Prepares log for reason edits
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who updated the reason"
    target_member : discord.Member
        "Member who's case reason was edited"
    case
        "Case object"
    old_reason : str
        "Old case reason"
        
    """
    embed = discord.Embed(title="Member Case Updated")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.blurple()
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Old reason", value=old_reason, inline=False)
    embed.add_field(name="New Reason", value=case.reason, inline=False)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_removepoints_log(mod, target_member, case):
    """Prepares log for point removal
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who removed the points"
    target_member : discord.Member
        "Member whose points were removed"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Points Removed")
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.color = discord.Color.blurple()
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Decrease", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_ban_log(mod, target_member, case):
    """Prepares ban log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who banned the member"
    target_member : discord.Member
        "Member who was banned"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Banned")
    embed.color = discord.Color.blue()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_unban_log(mod, target_member, case):
    """Prepares unban log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who unbanned the member"
    target_member : discord.Member
        "Member who was unbanned"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Unbanned")
    embed.color = discord.Color.blurple()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(name="Member", value=f'{target_member} ({target_member.id})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_kick_log(mod, target_member, case):
    """Prepares kick log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who kicked the member"
    target_member : discord.Member
        "Member who was kicked"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Kicked")
    embed.color = discord.Color.green()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=False)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_mute_log(mod, target_member, case):
    """Prepares mute log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who muted the member"
    target_member : discord.Member
        "Member who was muted"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Muted")
    embed.color = discord.Color.red()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Duration", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed

def prepare_unmute_log(mod, target_member, case):
    """Prepares unmute log
    
    Parameters
    ----------
    mod : discord.Member
        "Mod who unmuted the member"
    target_member : discord.Member
        "Member who was unmuted"
    case
        "Case object"
        
    """
    embed = discord.Embed(title="Member Unmuted")
    embed.color = discord.Color.green()
    embed.set_author(name=target_member, icon_url=target_member.display_avatar)
    embed.add_field(name="Member", value=f'{target_member} ({target_member.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{mod} ({mod.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {target_member.id}")
    embed.timestamp = case.date
    return embed
