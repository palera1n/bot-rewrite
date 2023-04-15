import discord

from discord.ext import commands

from utils import Cog
from utils.mod import add_kick_case, submit_public_log
from utils.services import guild_service


class NativeActionsListeners(Cog):
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        audit_logs = guild.audit_logs(limit=1, action=discord.AuditLogAction.kick)
        if audit_logs:
            add_kick_case(member, audit_logs[0].user, audit_logs[0].reason)
    
    @commands.Cog.listener()
    async def on_automod_action(self, ctx: discord.AutoModAction):
        await ctx.channel.send(f"{ctx.member.name} sent `{ctx.content}` and triggered automod!")
    