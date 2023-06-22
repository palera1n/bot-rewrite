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

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild.id != cfg.guild_id:
            return
        if message.author.bot:
            return

        tiktok = r"(https?://(?:www\.)?tiktok\.com/.*)"

        tiktok_match = re.search(tiktok, message.content)
        if tiktok_match:
            link = tiktok_match.group(1)
            quickvids_url = await self.quickvids(link)
            if quickvids_url:
                await message.edit(suppress=True)
                await message.reply(quickvids_url)
