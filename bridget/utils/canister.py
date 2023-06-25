import re
import discord

from datetime import datetime
from typing import List

from .menus import Menu

url_pattern = re.compile(
    r"((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")


default_repos = [
    "apt.bingner.com",
    "apt.elucubratus.com",
    "apt.procurs.us",
    "table.nickchan.gq",
    "ftp.sudhip.com/procursus",
    "repo.quiprr.dev/procursus",
    "apt.saurik.com",
    "apt.oldcurs.us",
    "repo.chimera.sh",
    "diatr.us/apt",
    "repo.theodyssey.dev",
    "repo.palera.in"
]


def tweak_embed_format(entry: dict) -> discord.Embed:
    titleKey = entry.get('name')
    description = discord.utils.escape_markdown(entry.get('description'))

    if entry.get('name') is None:
        titleKey = entry.get('package')
    embed = discord.Embed(title=titleKey, color=discord.Color.blue())
    embed.description = description[:200] + \
        "..." if len(description) > 200 else description

    if entry.get('author') is not None:
        embed.add_field(name="Author", value=discord.utils.escape_markdown(
            entry.get('author').split("<")[0]), inline=True)
    else:
        embed.add_field(name="Author", value=discord.utils.escape_markdown(
            entry.get('maintainer').split("<")[0]), inline=True)

    embed.add_field(name="Version", value=discord.utils.escape_markdown(
        entry.get('version') or "No Version"), inline=True)
    embed.add_field(name="Price", value=entry.get(
        "price") or "Free", inline=True)
    embed.add_field(
        name="Repo", value=f"[{entry.get('repository').get('name')}]({entry.get('repository').get('uri')})" or "No Repo", inline=True)
    embed.add_field(name="Bundle ID", value=entry.get(
        "package") or "Not found", inline=True)
    embed.add_field(name="Architecture", value=entry.get(
        "architecture") or "Not found", inline=True)

    if entry.get('tintColor') is None and entry.get('icon') is not None and url_pattern.match(entry.get('icon')):
        embed.color = discord.Color.blue()
    elif entry.get('tintColor') is not None:
        try:
            color = int(entry.get('tintColor').replace('#', '0x'), 0)
        except:
            color = discord.Color.blue()
        embed.color = color

    if entry.get('icon') is not None and url_pattern.match(entry.get('icon')):
        embed.set_thumbnail(url=entry.get('icon'))

    # this probably needs to be redone as stkc.win doesn't even resolve anymore (also you can just check repository.slug == bigboss)
    embed.set_footer(icon_url=f"{'https://assets.stkc.win/bigboss-sileo.png' if 'http://apt.thebigboss.org/repofiles/cydia/CydiaIcon.png' in entry.get('repository').get('uri')+'/CydiaIcon.png' else entry.get('repository').get('uri')+'/CydiaIcon.png'}",
                     text=f"Powered by Canister" or "No Package")
    embed.timestamp = datetime.now()

    return embed


async def format_tweak_page(ctx: discord.Interaction, entries: List[dict], current_page: int, all_pages: list) -> discord.Embed:
    """Formats the page for the tweak embed.

    Parameters
    ----------
    entries : List[dict]
        "The list of dictionaries for each tweak"
    all_pages : list
        "All entries that we will eventually iterate through"
    current_page : number
        "The number of the page that we are currently on"

    Returns
    -------
    discord.Embed
        "The embed that we will send"

    """
    entry = entries[0]
    ctx.repo = entry.get('repository').get('uri')
    ctx.depiction = entry.get('depiction')

    if entry.get('repository').get('isBootstrap'):
        ctx.repo = None

    embed = tweak_embed_format(entry)

    # this probably needs to be redone as stkc.win doesn't even resolve anymore (also you can just check repository.slug == bigboss)
    embed.set_footer(icon_url=f"{'https://assets.stkc.win/bigboss-sileo.png' if 'http://apt.thebigboss.org/repofiles/cydia/CydiaIcon.png' in entry.get('repository').get('uri')+'/CydiaIcon.png' else entry.get('repository').get('uri')+'/CydiaIcon.png'}",
                     text=f"Powered by Canister • Page {current_page}/{len(all_pages)}" or "No Package")
    return embed


class TweakMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, timeout_function=self.on_timeout)
        self.jump_button = JumpButton(self.ctx, len(self.pages), self)
        self.extra_buttons = []

    def refresh_button_state(self) -> None:
        if self.ctx.repo:
            extra_buttons = [
                discord.ui.Button(label='Add Repo to Sileo', emoji="<:sileo:679466569407004684>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={self.ctx.repo}&manager=sileo', style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Add Repo to Zebra', emoji="<:zebra:911433583032422420>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={self.ctx.repo}&manager=zebra', style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Other Package Managers', emoji="<:Add:947354227171262534>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={self.ctx.repo}', style=discord.ButtonStyle.url, row=1)
            ]
        else:
            extra_buttons = [
                discord.ui.Button(label='Cannot add default repo', emoji="<:sileo:679466569407004684>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={self.ctx.repo}&manager=sileo', disabled=True, style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Cannot add default repo', emoji="<:zebra:911433583032422420>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={self.ctx.repo}&manager=zebra', disabled=True, style=discord.ButtonStyle.url, row=1),
                discord.ui.Button(label='Cannot add default repo', emoji="<:Add:947354227171262534>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={self.ctx.repo}', style=discord.ButtonStyle.url, disabled=True, row=1)
            ]
        if self.ctx.depiction:
            extra_buttons.insert(0,
                                 discord.ui.Button(label='View Depiction', emoji="<:Depiction:947358756033949786>",
                                                   url=self.ctx.depiction, style=discord.ButtonStyle.url, row=1),
                                 )

        if len(self.pages) > 1:
            extra_buttons.append(self.jump_button)

        self.clear_items()
        for item in [self.previous, self.pause, self.next]:
            self.add_item(item)

        for button in extra_buttons:
            self.add_item(button)

        self.extra_buttons = extra_buttons

        super().refresh_button_state()

    def on_interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author # or gatekeeper.has(interaction.guild, interaction.user, 4)

    async def on_timeout(self) -> None:
        self.jump_button.disabled = True
        self.stopped = True
        await self.refresh_response_message()
        self.stop()


async def canister(ctx: discord.Interaction, whisper: bool, result) -> None:
    await TweakMenu(ctx, result, per_page=1, page_formatter=format_tweak_page, whisper=whisper, start_page=25, show_skip_buttons=False).start(ctx)


class TweakDropdown(discord.ui.Select):
    def __init__(self, author, entries, interaction, should_whisper):
        self.repo_icons = {
            "http://apt.thebigboss.org/repofiles/cydia": "<:colored_sileo_tweak_icon_bigboss:957470630956138496>",
            "https://repo.chariz.com": "<:colored_sileo_tweak_icon_chariz:957470675411537980>",
            "https://repo.chimera.sh": "<:colored_sileo_tweak_icon_chimera:957470798602440714>",
            "https://repo.dynastic.co": "<:colored_sileo_tweak_icon_dynasti:957470833952043038>",
            "https://apt.bingner.com": "<:colored_sileo_tweak_icon_elu:957471017578684496>",
            "https://havoc.app": "<:colored_sileo_tweak_icon_havoc:957471075942428723>",
            "https://repo.theodyssey.dev": "<:colored_sileo_tweak_icon_odyssey:957471133844799518>",
            "https://repo.packix.com": "<:colored_sileo_tweak_icon_packix:957471186638479470>",
            "https://apt.procurs.us": "<:colored_sileo_tweak_icon_procurs:957471236718460959>",
            "https://repo.twickd.com": "<:colored_sileo_tweak_icon_twickd:957471321351135233>",
        }
        self.author = author
        self.interaction = interaction
        self.raw_entries = entries
        self.should_whisper = should_whisper
        entries = entries[:24]
        self.current_entry = entries[0]
        self.entries = {entry.get("uuid"): entry for entry in entries}
        options = [discord.SelectOption(label=(option.get("name") or option.get('package'))[:100] or "No title", description=f"{option.get('author').split('<')[0] if option.get('author') is not None else option.get('maintainer').split('<')[0]} • {option.get('repository').get('name')}"[:100], value=option.get(
            "uuid"), emoji=self.repo_icons.get(option.get("repository").get("uri")) if self.repo_icons.get(option.get("repository").get("uri")) else "<:sileo_tweak_icon:957456295898779678>") for option in entries]

        if len(self.raw_entries) > 24:
            options.append(discord.SelectOption(
                label=f"View {len(self.raw_entries) - 24} more results...", value="view_more"))
        super().__init__(placeholder='Pick a tweak to view...',
                         min_values=1, max_values=1, options=options)

    def start(self, ctx: discord.Interaction) -> None:
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.author: # and not gatekeeper.has(interaction.guild, interaction.user, 4):
            return

        self.ctx = interaction

        if self.values[0] == "view_more":
            await canister(self.ctx, self.should_whisper, self.raw_entries)
            self._view.stop()
            return

        selected_value = self.entries.get(self.values[0])
        if selected_value is None:
            return

        self.refresh_view(selected_value)
        await self.ctx.response.edit_message(embed=tweak_embed_format(selected_value), view=self._view)

    async def on_timeout(self) -> None:
        self.disabled = True
        self.placeholder = "Timed out"
        if isinstance(self.ctx, discord.Interaction):
            await self.ctx.response.edit(view=self._view)
        else:
            await self.ctx.message.edit(view=self._view)

    def generate_buttons(self, entry: dict) -> List[discord.ui.Button]:
        repo = entry.get('repository').get('uri')
        depiction = entry.get('depiction')

        if entry.get('repository').get('isBootstrap'):
            repo = None

        if repo is not None:
            extra_buttons = [
                discord.ui.Button(label='Add Repo to Sileo', emoji="<:sileo:679466569407004684>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={repo}&manager=sileo', style=discord.ButtonStyle.url),
                discord.ui.Button(label='Add Repo to Zebra', emoji="<:zebra:911433583032422420>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={repo}&manager=zebra', style=discord.ButtonStyle.url),
                discord.ui.Button(label='Other Package Managers', emoji="<:Add:947354227171262534>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={repo}', style=discord.ButtonStyle.url)
            ]
        else:
            extra_buttons = [
                discord.ui.Button(label='Cannot add default repo', emoji="<:sileo:679466569407004684>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={repo}&manager=sileo', disabled=True, style=discord.ButtonStyle.url),
                discord.ui.Button(label='Cannot add default repo', emoji="<:zebra:911433583032422420>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={repo}&manager=zebra', disabled=True, style=discord.ButtonStyle.url),
                discord.ui.Button(label='Cannot add default repo', emoji="<:Add:947354227171262534>",
                                  url=f'https://repos.slim.rocks/repo/?repoUrl={repo}', disabled=True, style=discord.ButtonStyle.url)
            ]
        if depiction is not None:
            extra_buttons.insert(0,
                                 discord.ui.Button(label='View Depiction', emoji="<:Depiction:947358756033949786>",
                                                   url=depiction, style=discord.ButtonStyle.url),
                                 )
        return extra_buttons

    def refresh_view(self, entry: dict) -> None:
        extra_buttons = self.generate_buttons(entry)
        self._view.clear_items()

        if len(self.raw_entries) > 1:
            self._view.add_item(self)

        for button in extra_buttons:
            self._view.add_item(button)


class JumpButton(discord.ui.Button):
    def __init__(self, ctx, max_page: int, tmb):
        super().__init__(style=discord.ButtonStyle.primary,
                         emoji="<:RightArrowCurvingUp:957270226167296090>")
        self.max_page = max_page
        self.ctx = ctx
        self.tmb = tmb
        self.row = 2

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.tmb.ctx.author:
            return

        self.ctx.interaction = interaction
        modal = JumpModal(self.tmb.current_page, self.max_page)
        await interaction.response.send_modal(modal)
        await modal.wait()

        if modal.page.value is not None:
            try:
                res = int(modal.page.value)
            except ValueError:
                await self.ctx.send_warning("Invalid page number!", followup=True, ephemeral=True)
                return

            if res < 0 or res > self.max_page:
                await self.ctx.send_warning("Invalid page number!", followup=True, ephemeral=True)
                return

            self.tmb.current_page = res
            await self.tmb.refresh_response_message()
            await self.ctx.send_success(f"Jumped to page {res}!", followup=True, ephemeral=True)


class JumpModal(discord.ui.Modal):
    def __init__(self, current_page, max_page):
        super().__init__(title=f"Jump to Page (currently {current_page})")
        self.page = discord.ui.TextInput(
            label="Page", placeholder=f"Between 1 and {max_page}")
        self.add_item(self.page)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.send_message()
        except:
            pass

