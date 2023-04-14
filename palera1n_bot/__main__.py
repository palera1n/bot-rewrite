from utils.startup_checks import checks as startup_checks
import discord
from discord.ext import commands
import os
import dotenv

import mongoengine

mongoengine.connect('botty', host='localhost', port=27017)


dotenv.load_dotenv()

for check in startup_checks:
    check()


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


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
