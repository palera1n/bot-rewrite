import discord
from discord.enums import AutoModRuleActionType

from discord.ext import commands
from datetime import datetime

from utils import Cog
from utils.mod import add_kick_case, add_mute_case, add_ban_case, add_unban_case
from utils.services import guild_service


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
            await channel.send(embed=await add_kick_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member) -> None:
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)]
        if audit_logs and audit_logs[0].target == member:
            channel = guild.get_channel(
                guild_service.get_guild().channel_public)
            await channel.send(embed=await add_ban_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, member: discord.User) -> None:
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban, after=member.created_at)]
        if audit_logs and audit_logs[0].target == member:
            channel = guild.get_channel(
                guild_service.get_guild().channel_public)
            await channel.send(embed=await add_unban_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if not before.is_timed_out() and after.is_timed_out():
            channel = self.bot.get_channel(
                guild_service.get_guild().channel_public)
            # get reason from audit log
            audit_logs = [audit async for audit in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update, after=after.joined_at)]
            if audit_logs and audit_logs[0].target == after:
                await channel.send(embed=await add_mute_case(after, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild(), self.bot))

    @commands.Cog.listener()
    async def on_automod_action(self, ctx: discord.AutoModAction):
        print(ctx)
        rule = await ctx.fetch_rule()
        member = ctx.guild.get_member(ctx.user_id)
        if guild_service.get_guild().role_helper not in rule.exempt_role_ids and ctx.action.type == AutoModRuleActionType.send_alert_message:
            embed = discord.Embed(title="Filter word detected")
            embed.color = discord.Color.red()
            embed.set_thumbnail(url=member.display_avatar)
            embed.add_field(
                name="User", value=f'{member} ({member.mention})', inline=True)
            embed.add_field(name="Message", value=ctx.content, inline=True)
            embed.add_field(name="Filtered word", value=ctx.matched_content, inline=True)
            embed.timestamp = datetime.now()
            embed.set_footer(text=f"{member.name}#{member.discriminator}")
            channel = ctx.guild.get_channel(guild_service.get_guild().channel_reports)
            await channel.send(content=f"<@&{guild_service.get_guild().role_reportping}>",
                embed=embed, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True)
            )
        elif ctx.action.type == AutoModRuleActionType.timeout:
            # check role and ban for raid phrase
            if guild_service.get_guild().role_memberplus not in [ x.id for x in member.roles ]:
                await ctx.guild.get_member(ctx.user_id).ban(reason="Raid phrase detected")

