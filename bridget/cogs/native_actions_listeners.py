import discord
from discord.ext import commands
from utils.mod import add_kick_case, submit_public_log
from utils.services import guild_service


class NativeActionsListeners(commands.Cog):
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        audit_logs = [entry async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick)]
        if audit_logs and audit_logs[0].target.id == member.id:
            submit_public_log(add_kick_case(member, audit_logs[0].user, "No reason." if audit_logs[0].reason is None else audit_logs[0].reason, guild_service.get_guild()))
            