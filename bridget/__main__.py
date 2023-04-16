import asyncio
import logging
import discord
import mongoengine

from os import getenv
mongoengine.connect('bridget', host=getenv("DB_HOST"), port=int(getenv("DB_PORT")))
from discord.ext import commands
from discord import app_commands

from utils import send_error
from utils.config import cfg
from utils.startup_checks import checks
from cogs import Logging, Mod, NativeActionsListeners, Say, Sync, Tags, Unshorten


for check in checks:
    check()

bot = commands.Bot(
    command_prefix=cfg.prefix,
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
)
bot.remove_command("help")

asyncio.run(bot.add_cog(Logging(bot)))
asyncio.run(bot.add_cog(Mod(bot)))
asyncio.run(bot.add_cog(NativeActionsListeners(bot)))
asyncio.run(bot.add_cog(Say(bot)))
asyncio.run(bot.add_cog(Sync(bot)))
asyncio.run(bot.add_cog(Tags(bot)))
asyncio.run(bot.add_cog(Unshorten(bot)))

@bot.tree.error
async def app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError):
        error = error.original

    if isinstance(error, discord.errors.NotFound):
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=f"Sorry {interaction.user.mention}, it looks like I took too long to respond to you! If I didn't do what you wanted in time, please try again."), delete_after=5)
        return

    if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, app_commands.TransformerError)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, app_commands.MissingPermissions)
            or isinstance(error, app_commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
            or isinstance(error, app_commands.NoPrivateMessage)):
        await send_error(interaction, error)
    else:
        try:
            raise error
        except:
            tb = traceback.format_exc()
            logger.error(tb)
            if len(tb.split('\n')) > 8:
                tb = '\n'.join(tb.split('\n')[-8:])

            tb_formatted = tb
            if len(tb_formatted) > 1000:
                tb_formatted = "...\n" + tb_formatted[-1000:]

            await send_error(interaction, f"`{error}`\n```{tb_formatted}```", delete_after=5)

bot.run(getenv("TOKEN"))