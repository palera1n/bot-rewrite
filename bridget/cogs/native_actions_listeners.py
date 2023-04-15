import discord
from discord.ext import commands
from utils.mod import add_kick_case


class NativeActionsListeners(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_remove(member: discord.Member):
        guild = member.guild
        audit_logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()
        if audit_logs:
            add_kick_case(member, audit_logs[0].user, audit_logs[0].reason)