import discord
from discord.ext import commands
import os
import dotenv
dotenv.load_dotenv()



bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


import cogs.warns


@bot.event
async def on_ready():
    #await bot.add_cog(cogs.warns.Warns(bot))
    await bot.add_cog(cogs.warns.Warns)
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def ping(ctx):
    """Respond with pong"""
    await ctx.send('Pong!')







bot.run(os.getenv('TOKEN'))

