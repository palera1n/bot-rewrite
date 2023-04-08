import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


import cogs.warns


@bot.event
async def on_ready():
    #await bot.add_cog(cogs.warns.Warns(bot))
    await cogs.warns.setup(bot)
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.hybrid_command()
async def ping(ctx):
    """Respond with pong"""
    await ctx.send('Pong!')

@bot.hybrid_command(name='sync', description='Owner only')
async def sync(ctx):
    if ctx.author.id == 825691714383511582:
        await bot.tree.sync(guild=ctx.guild)
        print('Command tree synced.')
    else:
        await ctx.send('You must be the owner to use this command!')






bot.run(os.getenv('TOKEN'))

