import re
import discord

from discord import app_commands
from discord.ext import commands

from utils.config import cfg
from utils.enums import PermissionLevel
from utils.services import guild_service
from utils.fetchers import canister_fetch_repos, canister_search_package
from utils.canister import TweakDropdown, tweak_embed_format
from utils.utils import send_error
from utils.autocomplete import repo_autocomplete

class Canister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return

        author = message.guild.get_member(message.author.id)
        if author is None:
            return

        pattern = re.compile(
            r".*?(?<!\[)+\[\[((?!\s+)([\w+\ \&\+\-\<\>\#\:\;\%\(\)]){2,})\]\](?!\])+.*")
        if not pattern.match(message.content):
            return

        matches = pattern.findall(message.content)
        if not matches:
            return

        search_term = matches[0][0].replace('[[', '').replace(']]', '')
        if not search_term:
            return

        ctx = await self.bot.get_context(message)

        async with ctx.typing():
            result = list(await canister_search_package(search_term))

        if not result:
            embed = discord.Embed(
                title=":(\nI couldn't find that package", color=discord.Color.red())
            embed.description = f"Try broadening your search query."
            await ctx.send(embed=embed, delete_after=8)
            return

        view = discord.ui.View(timeout=30)
        td = TweakDropdown(author, result, interaction=False,
                           should_whisper=False)
        td._view = view
        view.add_item(td)
        td.refresh_view(result[0])
        view.on_timeout = td.on_timeout
        embed = tweak_embed_format(result[0])
        message = await message.reply(embed=embed, view=view)
        new_ctx = await self.bot.get_context(message)
        td.start(new_ctx)

    @app_commands.command()
    async def package(self, ctx: discord.Interaction, query: str) -> None:
        """Search for a jailbreak tweak or package

        Args:
            ctx (discord.ctx): Context
            query (str): Name of package to search for
        """

        if len(query) < 2:
            raise commands.BadArgument("Please enter a longer query.")

        should_whisper = False
        if not PermissionLevel.MOD == ctx.user and ctx.channel_id == guild_service.get_guild().channel_general:
            should_whisper = True

        await ctx.response.defer(ephemeral=should_whisper)
        result = list(await canister_search_package(query))

        if not result:
            embed = discord.Embed(
                title=":(\nI couldn't find that package", color=discord.Color.red())
            embed.description = f"Try broadening your search query."
            await ctx.response.send_message(embed=embed)
            return

        view = discord.ui.View(timeout=30)
        td = TweakDropdown(ctx.user, result, interaction=True,
                           should_whisper=should_whisper)
        td._view = view
        view.on_timeout = td.on_timeout
        view.add_item(td)
        td.refresh_view(result[0])
        await ctx.followup.send(embed=tweak_embed_format(result[0]), view=view)
        td.start(ctx)

    @app_commands.command()
    @app_commands.autocomplete(query=repo_autocomplete)
    async def repo(self, ctx: discord.Interaction, query: str) -> None:
        """Search for a tweak repository

        Args:
            ctx (discord.ctx): Context
            query (str): Name of repository to search for
        """

        repos = await canister_fetch_repos()
        matches = [repo for repo in repos if repo.get("slug") and repo.get(
            "slug") is not None and repo.get("slug").lower() == query.lower()]
        if not matches:
            await send_error(ctx, "That repository isn't registered with Canister's database.")
            return

        repo_data = matches[0]

        embed = discord.Embed(title=repo_data.get(
            'name'), color=discord.Color.blue())
        embed.add_field(name="URL", value=repo_data.get('uri'), inline=True)
        embed.set_thumbnail(url=f'{repo_data.get("uri")}/CydiaIcon.png')
        embed.set_footer(text="Powered by Canister")

        this_repo = repo_data.get("uri")
        view = discord.ui.View()

        if repo_data['isBootstrap']:
            [view.add_item(item) for item in [
                discord.ui.Button(label='Cannot add default repo', emoji="<:Sileo:959128883498729482>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={this_repo}&manager=sileo', disabled=True, style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Cannot add default repo', emoji="<:Zeeb:959129860603801630>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={this_repo}&manager=zebra', disabled=True, style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Cannot add default repo', emoji="<:Add:947354227171262534>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={this_repo}', style=discord.ButtonStyle.url, disabled=True, row=1)
            ]]
        else:
            [view.add_item(item) for item in [
                discord.ui.Button(label='Add Repo to Sileo', emoji="<:Sileo:959128883498729482>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={this_repo}&manager=sileo', style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Add Repo to Zebra', emoji="<:Zeeb:959129860603801630>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={this_repo}&manager=zebra', style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Other Package Managers', emoji="<:Add:947354227171262534>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={this_repo}', style=discord.ButtonStyle.url, row=1)
            ]]

        await ctx.response.send_message(embed=embed, view=view)

