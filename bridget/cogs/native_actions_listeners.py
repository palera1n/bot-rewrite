import argparse
import discord

from discord.ext import commands
from datetime import datetime
from discord.utils import format_dt, escape_markdown
from discord.enums import AutoModRuleActionType
from bridget.model.infraction import Infraction

from utils import Cog
from utils.mod import add_kick_infraction, add_mute_infraction, add_ban_infraction, add_unban_infraction, add_unmute_infraction, notify_user_warn_noctx, prepare_warn_log, submit_public_log, submit_public_log_noctx
from utils.services import guild_service, user_service
from utils.utils import audit_logs_multi, get_warnpoints
from utils.views import AutoModReportView

async def warn(bot: commands.Bot, target_member: discord.Member, mod: discord.Member, points: int, reason: str):
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
    cur_points = get_warnpoints(db_user)

    log = prepare_warn_log(mod, target_member, infraction)
    log.add_field(name="Current points", value=f"{cur_points}/10", inline=True)

    dmed = await notify_user_warn_noctx(target_member, mod, db_user, db_guild, cur_points, log)
    await submit_public_log_noctx(bot, db_guild, target_member, log, dmed)

class StringWithFlags:
    def __init__(self, value):
        self.value = value

def parse_string_with_flags(string):
    return StringWithFlags(string)

class StringWithFlags:
    def __init__(self, value: str):
        self.value: str = value

def parse_string_with_flags(string: str):
    return StringWithFlags(string)

class NativeActionsListeners(Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        guild = member.guild
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick, after=member.joined_at)]
        if audit_logs and audit_logs[0].target == member:
            channel = member.guild.get_channel(
                guild_service.get_guild().channel_public)
            await channel.send(embed=await add_kick_infraction(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member) -> None:
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)]
        if audit_logs and audit_logs[0].target == member:
            channel = guild.get_channel(
                guild_service.get_guild().channel_public)
            await channel.send(embed=await add_ban_infraction(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, member: discord.User) -> None:
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban, after=member.created_at)]
        if audit_logs and audit_logs[0].target == member:
            channel = guild.get_channel(
                guild_service.get_guild().channel_public)
            await channel.send(embed=await add_unban_infraction(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if not before.is_timed_out() and after.is_timed_out():
            channel = self.bot.get_channel(
                guild_service.get_guild().channel_public)
            # get reason from audit log
            audit_logs = await audit_logs_multi(before.guild, [ discord.AuditLogAction.member_update, discord.AuditLogAction.automod_timeout_member ], limit=1, after=after.joined_at)
            if audit_logs and audit_logs[0].target == after:
                print("hello")
                parser = argparse.ArgumentParser(exit_on_error=False, usage="")
                parser.add_argument("-w", "--warn", type=int, default=1)
                parser.add_argument("message", type=str, nargs='*')
                try:
                    strparse = parser.parse_args(audit_logs[0].reason.split())
                except SystemExit as e:
                    await (await audit_logs[0].user.create_dm()).send("Your mute had an exception! The error was probably an invalid flag. Unmuting the user!")
                    await after.edit(timed_out_until=None, reason="A SystemExit was triggered by argparse (probably broken flags)")
                    return
                print(type(strparse))
                await channel.send(embed=await add_mute_infraction(after, audit_logs[0].user, "No reason." if not ''.join(strparse.message) else ''.join(strparse.message), guild_service.get_guild(), self.bot))
                print("before warn")
                await warn(self.bot, after, audit_logs[0].user, strparse.warn, "Automatic point addition")
        elif before.is_timed_out() and not after.is_timed_out():
            channel = self.bot.get_channel(
                guild_service.get_guild().channel_public)
            # get reason from audit log
            audit_logs = await audit_logs_multi(before.guild, [ discord.AuditLogAction.member_update, discord.AuditLogAction.automod_timeout_member ], limit=1, after=after.joined_at)
            if audit_logs and audit_logs[0].target == after:
                await channel.send(embed=await add_unmute_infraction(after, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_automod_action(self, ctx: discord.AutoModAction) -> None:
        rule = await ctx.fetch_rule()
        member = ctx.guild.get_member(ctx.user_id)

        # filter with mod+ bypass
        if ctx.action.type == discord.AutoModRuleActionType.send_alert_message and rule.name.endswith('🚨'):
            print(ctx, rule)
            await automod_fancy_embed(self.bot, ctx, rule, member)
        elif ctx.action.type == AutoModRuleActionType.timeout:
            # check role and ban for raid phrase
            if guild_service.get_guild().role_memberplus not in [ x.id for x in member.roles ]:
                await ctx.guild.get_member(ctx.user_id).ban(reason="Raid phrase detected")


async def automod_fancy_embed(bot: discord.BotIntegration, ctx: discord.AutoModAction, rule: discord.AutoModRule, member: discord.Member) -> None:
    # embed
    embed = discord.Embed(title="Filter word detected")
    embed.color = discord.Color.red()
    embed.set_thumbnail(url=member.display_avatar)
    embed.add_field(
        name="Member", value=f'{member} ({member.mention})', inline=True)
    embed.add_field(
        name="Channel", value=ctx.channel.mention, inline=True)
    embed.add_field(name="Message", value=ctx.content, inline=False)
    embed.add_field(name="Filtered word", value=ctx.matched_content, inline=True)
    embed.timestamp = datetime.now()
    embed.set_footer(text=f"{member}")
    embed.add_field(
        name="Join date",
        value=f"{format_dt(member.joined_at, style='F')} ({format_dt(member.joined_at, style='R')})",
        inline=True)
    embed.add_field(
        name="Created",
        value=f"{format_dt(member.created_at, style='F')} ({format_dt(member.created_at, style='R')})",
        inline=True)
    embed.add_field(
        name="Warn points",
        value=user_service.get_user(ctx.user_id).warn_points,
        inline=True)

    # buttons
    view = AutoModReportView(member, bot)

    # send embed and buttons (roles=True to enable mod ping)
    channel = ctx.guild.get_channel(guild_service.get_guild().channel_reports)
    await channel.send(content=f"<@&{guild_service.get_guild().role_reportping}>",
        embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True)
    )

