import discord
from discord.ext import commands
import mongoengine

class NativeActionListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} has joined the server")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f"{member} has left the server")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        print(f"{member} has been banned from {guild}")
