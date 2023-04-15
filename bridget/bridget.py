import asyncio
import logging
import discord
import mongoengine

from os import getenv
from ruamel.yaml import YAML
from discord.ext import commands
from platformdirs import PlatformDirs

from .utils import checks
from .cogs import Say, Sync


def main() -> None:
    """Main function"""
    
    mongoengine.connect('bridget', host='localhost', port=27017)
    for check in checks:
        check()

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
    )

    asyncio.run(bot.add_cog(Say(bot, config)))
    asyncio.run(bot.add_cog(Sync(bot, config)))

    bot.run(getenv("TOKEN"), log_level=logging.DEBUG)
