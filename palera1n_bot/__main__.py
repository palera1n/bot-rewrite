import discord
from discord.ext import commands
import os
import dotenv
import utils.database

dotenv.load_dotenv()



bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


import cogs.warns


bot.load_extension('cogs.warns')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@commands.command
async def ping(ctx):
    """Respond with pong"""
    await ctx.send('Pong!')







bot.run(os.getenv('TOKEN'))

