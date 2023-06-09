import discord

from discord.ext import commands

from utils.fetchers import fetch_remote_json, fetch_remote_file
from utils.services import guild_service
from model.issues import Issue
from cogs.issues import prepare_issue_embed, prepare_issue_view

class LogParsing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
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

    async def reply_with_issue(self, msg: discord.Message, issue: Issue) -> None:
        _file = issue.image.read()
        if _file is not None:
            _file = discord.File(
                BytesIO(_file),
                filename="image.gif" if issue.image.content_type == "image/gif" else "image.png")
        else:
            _file = discord.utils.MISSING

        await msg.reply(embed=prepare_issue_embed(issue), view=prepare_issue_view(issue), file=_file)

    async def do_panic_log(self, msg: discord.Message, att) -> None:
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
                for issue in guild_service.get_guild().issues:
                    if issue.panic_string is not None and len(issue.panic_string) > 0 and issue.panic_string in string:
                        await self.reply_with_issue(msg, issue)

    async def do_log_file(self, msg: discord.Message, att) -> None:
        text = await fetch_remote_file(att.url)
        if text is not None:
            if not "```" in text or "@everyone" in text or "@here" in text:
                string = '\n'.join(text.splitlines()[-10:])
                await msg.reply(f"Hey, it looks like this is a palera1n failure log!\n\nHere is the last 10 lines to help debuggers:```{discord.utils.escape_markdown(string)}```")
