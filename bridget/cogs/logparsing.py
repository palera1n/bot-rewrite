import discord

from discord.ext import commands

from utils.fetchers import fetch_remote_json, fetch_remote_file

class LogParsing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """When an .ips file is posted, check if its valid JSON and a panic log"""

        if msg.author.bot:
            return

        if not msg.attachments:
            return

        att = msg.attachments[0]
        if att.filename.endswith(".ips"):
            await self.do_panic_log(msg, att)
        elif att.filename.endswith(".log") and att.filename.startswith("FAIL"):
            await self.do_log_file(msg, att)

    async def do_panic_log(self, msg: discord.Message, att):
        json = await fetch_remote_json(att.url)
        if json is not None:
            if "panicString" in json:
                string = json['panicString'].split("\n")[0]

            if "build" in json:
                build = json['build'].split("\n")[0]

            if "product" in json:
                product = json['product'].split("\n")[0]

            if string == "" or build == "" or product == "":
                return

            if (not "```" in string or "@everyone" in string or "@here" in string) and (not "`" in build or "@everyone" in build or "@here" in build) and (not "`" in product or "@everyone" in product or "@here" in product):
                await msg.reply(f"Hey, it looks like this is a panic log for build: `{discord.utils.escape_markdown(build)}` on a `{discord.utils.escape_markdown(product)}`!\n\nHere is the panic string:```{discord.utils.escape_markdown(string)}```")

    async def do_log_file(self, msg: discord.Message, att):
        text = await fetch_remote_file(att.url)
        if text is not None:
            if not "```" in text or "@everyone" in text or "@here" in text:
                string = '\n'.join(text.splitlines()[-10:])
                await msg.reply(f"Hey, it looks like this is a palera1n failure log!\n\nHere is the last 10 lines to help debuggers:```{discord.utils.escape_markdown(string)}```")
