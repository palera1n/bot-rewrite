import discord
from discord.ext import commands



class NativeActionsListeners(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_remove(member: discord.Member):
        # check audit log for kick action
        guild = member.guild
        audit_logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()
        if audit_logs:
            
