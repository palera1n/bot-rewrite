import re
import aiohttp
import discord

from discord.utils import get
from discord.ext import commands

from utils import Cog, reply_success


class Unshorten(Cog):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return


        # Return in DMs
        if message.guild == None:
            return

        emoji = get(message.guild.emojis, name="loading")
        regex = r"\b(?:https?:\/\/(?:t\.co|bit\.ly|goo\.gl|fb\.me|tinyurl\.com|j\.mp|is\.gd|v\.gd|git\.io)\/[\w-]+)\b"

        async with aiohttp.ClientSession() as session:
            for link in re.findall(regex, message.content):
                await message.add_reaction(emoji)
                async with session.head(link, allow_redirects=True) as res:
                    await reply_success(message, description=f"Hey, here's where this short link actually goes to!\n{res.url}")
                    await message.remove_reaction(emoji, self.bot.user)
