import discord
from discord.ext import commands
import os

async def check_invokee(ctx: discord.ApplicationContext, user: discord.Member, bot: commands.Bot):
    top_role = ctx.author.roles[-1]

    if ctx.author.id == user:
        return False
    if top_role.position < user.roles[-1].position:
        return False
    if user.id == bot.user.id:
        return False
    return True
    
