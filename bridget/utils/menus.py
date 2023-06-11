import inspect
import discord

from discord import ui
from typing import Callable, Generator, Optional


class Menu(ui.View):
    def __init__(self,
                 ctx: discord.Interaction,
                 entries: list,
                 per_page: int,
                 page_formatter: Callable[[discord.Interaction,
                                           list,
                                           int,
                                           list],
                                          None],
                 whisper: bool,
                 show_skip_buttons: bool = True,
                 start_page: int=1,
                 timeout_function=None) -> None:
        super().__init__(timeout=60)

        self.ctx = ctx
        self.is_interaction = isinstance(ctx, discord.Interaction)

        """Initializes a menu"""
        def chunks(lst: list, n: int) -> Generator:
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        self.pages = list(chunks(entries, per_page))
        self.per_page = per_page
        self.page_formatter = page_formatter
        self.whisper = whisper
        self.show_skip_buttons = show_skip_buttons
        self.current_page = start_page
        self.on_timeout = timeout_function or self.on_timeout

        self.stopped = False
        self.page_cache = {}

        if not self.show_skip_buttons:
            self.remove_item(self.first)
            self.remove_item(self.last)

    async def start(self) -> None:
        embed = await self.generate_next_embed()
        self.refresh_button_state()
        await self.ctx.response.send_message(embed=embed, view=self, ephemeral=self.whisper)

        #await self.refresh_response_message(self.ctx)

    async def generate_next_embed(self) -> Optional[discord.Embed]:
        if self.current_page in self.page_cache:
            return self.page_cache.get(self.current_page)

        if inspect.iscoroutinefunction(self.page_formatter):
            embed = await self.page_formatter(self.ctx, self.pages[self.current_page - 1], self.current_page, self.pages)
        else:
            embed = self.page_formatter(self.ctx,
                                        self.pages[self.current_page - 1],
                                        self.current_page,
                                        self.pages)

        self.page_cache[self.current_page] = embed
        return embed

    def refresh_button_state(self) -> None:
        built_in_buttons = [self.first, self.previous,
                            self.pause, self.next, self.last]

        if len(self.pages) == 1:
            for button in built_in_buttons:
                self.remove_item(button)
            self.stop()
            return
        elif self.stopped:
            for button in built_in_buttons:
                button.disabled = True
            return

        self.first.disabled = self.current_page == 1
        self.previous.disabled = self.current_page == 1
        self.next.disabled = self.current_page == len(self.pages)
        self.last.disabled = self.current_page == len(self.pages)

    async def refresh_response_message(self, interaction: discord.Interaction = None) -> None:
        embed = await self.generate_next_embed()
        self.refresh_button_state()

        if interaction is not None:  # we want to edit, due to button press
            await interaction.response.edit_message(embed=embed, view=self)
        elif self.ctx.response.is_done(): # i guess this fixes it, too lazy to test it - Jan
            await self.ctx.response.edit_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        self.stopped = True
        self.refresh_button_state()
        await self.refresh_response_message()
        self.stop()

    @ui.button(emoji='<:Arrow_Icon_HardLeft:957676574918975578>',
               style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def first(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if self.on_interaction_check(interaction):
            self.current_page = 1
            await self.refresh_response_message(interaction)

    @ui.button(emoji='<:ArrowLeft:957270073817583636>',
               style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if self.on_interaction_check(interaction):
            self.current_page -= 1
            await self.refresh_response_message(interaction)

    @ui.button(emoji='<:Stop:957270274691194891>',
               style=discord.ButtonStyle.blurple, row=2)
    async def pause(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if self.on_interaction_check(interaction):
            await self.on_timeout()
            await self.refresh_response_message(interaction)

    @ui.button(emoji='<:ArrowRight:957270142360895548>',
               style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def next(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if self.on_interaction_check(interaction):
            self.current_page += 1
            await self.refresh_response_message(interaction)

    @ui.button(emoji='<:Arrow_Icon_HardRight:957676487060893726>',
               style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def last(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if self.on_interaction_check(interaction):
            self.current_page = len(self.pages)
            await self.refresh_response_message(interaction)

    def on_interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.user

class PFPView(discord.ui.View):
    def __init__(self, ctx: discord.Interaction, embed=discord.Embed):
        super().__init__(timeout=30)
        self.embed = embed
        self.ctx = ctx

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.ctx.response.edit_message(embed=self.embed, view=self)


class PFPButton(discord.ui.Button):
    def __init__(self, ctx: discord.Interaction, member: discord.Member):
        super().__init__(label="Show other avatar", style=discord.ButtonStyle.primary)
        self.ctx = ctx
        self.member = member
        self.other = False

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.ctx.author:
            return
        if not self.other:
            avatar = self.member.guild_avatar
            self.other = not self.other
        else:
            avatar = self.member.avatar or self.member.default_avatar
            self.other = not self.other

        embed = interaction.message.embeds[0]
        embed.set_image(url=avatar.replace(size=4096))

        animated = ["gif", "png", "jpeg", "webp"]
        not_animated = ["png", "jpeg", "webp"]

        def fmt(format_) -> str:
            return f"[{format_}]({avatar.replace(format=format_, size=4096)})"

        if avatar.is_animated():
            embed.description = f"View As\n {'  '.join([fmt(format_) for format_ in animated])}"
        else:
            embed.description = f"View As\n {'  '.join([fmt(format_) for format_ in not_animated])}"

        self.view.embed = embed
        await interaction.response.edit_message(embed=embed)
