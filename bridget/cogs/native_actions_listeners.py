import discord

from discord.ext import commands

from utils import Cog
from utils.mod import add_kick_case, submit_public_log, add_ban_case, add_unban_case
from utils.services import guild_service


class NativeActionsListeners(Cog):
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick, after=member.joined_at)]
        if audit_logs and audit_logs[0].target == member:
            channel = member.guild.get_channel(guild_service.get_guild().channel_public)
            await channel.send(embed=add_kick_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild()))
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)]
        if audit_logs and audit_logs[0].target == member:
            channel = guild.get_channel(guild_service.get_guild().channel_public)
            await channel.send(embed=await add_ban_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild()))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, member: discord.User):
        audit_logs = [audit async for audit in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban, after=member.created_at)]
        if audit_logs and audit_logs[0].target == member:
            channel = guild.get_channel(guild_service.get_guild().channel_public)
            await channel.send(embed=add_unban_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild()))

    @commands.Cog.listener()
    async def on_automod_action(self, ctx: discord.AutoModAction):
        await ctx.channel.send(f"{ctx.member.name} sent `{ctx.content}` and triggered automod!")
    