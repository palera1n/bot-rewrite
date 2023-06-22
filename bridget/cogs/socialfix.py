import asyncio
import aiohttp
import json
import discord
import re

from discord.ext import commands

from utils import Cog
from utils.config import cfg


class SocialFix(Cog):
    async def quickvids(self, tiktok_url):
        headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            url = 'https://api.quickvids.win/v1/shorturl/create'
            data = {'tiktok_url': tiktok_url}
            async with session.post(url, json=data) as response:
                text = await response.text()
                data = json.loads(text)
                quickvids_url = data['quickvids_url']
                return quickvids_url

    async def vxtwitter(self, twitter_url):
        return twitter_url.replace("twitter.com", "vxtwitter.com", 1)

    async def ddinstagram(self, insta_url):
        return insta_url.replace("instagram.com", "ddinstagram.com", 1)

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild.id != cfg.guild_id:
            return
        if message.author.bot:
            return

        fixes = [
            {
                "regex": r"(https?://(?:www\.)?tiktok\.com/.*)",
                "function": self.quickvids
            },
            {
                "regex": r"(https?://twitter\.com/.*)",
                "function": self.vxtwitter
            },
            {
                "regex": r"(https?://(?:www\.)?instagram\.com/.*)",
                "function": self.ddinstagram
            }
        ]

        for fix in fixes:
            fix_match = re.search(fix["regex"], stringy);
            if fix_match:
                fixed_url = await fix["function"](fix_match.group(1))
                if fixed_url:
                    await message.edit(suppress=True)
                    await message.reply(fixed_url)
                    break
