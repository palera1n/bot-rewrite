import asyncio
import logging
import discord
import mongoengine

from os import getenv

mongoengine.connect('bridget', host=getenv("DB_HOST"), port=int(getenv("DB_PORT")))

from ruamel.yaml import YAML
from discord.ext import commands
from platformdirs import PlatformDirs

from utils import checks, cfg
from cogs import Say, Sync, Mod, NativeActionsListeners, Logging


def main() -> None:
    """Main function"""
    
    for check in checks:
        check()

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=cfg.prefix,
        intents=intents,
        allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
    )

    asyncio.run(bot.add_cog(Say(bot)))
    asyncio.run(bot.add_cog(Sync(bot)))
    asyncio.run(bot.add_cog(Mod(bot)))
    asyncio.run(bot.add_cog(NativeActionsListeners(bot)))
    asyncio.run(bot.add_cog(Logging(bot)))
    
    bot.run(getenv("TOKEN"))

if __name__ == "__main__":
    main()