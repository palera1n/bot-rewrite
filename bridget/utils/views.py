import discord
import discord.ui as ui

from utils.mod import warn
from utils.modals import AutoModWarnButtonModal, ReasonModal

class AutoModReportView(ui.View):
    member: discord.Member
    bot: discord.BotIntegration

    @ui.button(label='Dismiss', style=discord.ButtonStyle.green)
    async def dismiss(self, ctx: discord.Interaction, button: ui.Button) -> None:
        await ctx.message.delete()
        await ctx.response.defer()

    @ui.button(label='Warn', style=discord.ButtonStyle.red)
    async def warn(self, ctx: discord.Interaction, button: ui.Button) -> None:
        modal = AutoModWarnButtonModal(bot=self.bot, ctx=ctx, author=ctx.user, user=self.member)
        await ctx.response.send_modal(modal)
        await modal.wait()

        await warn(ctx, target_member=self.member, mod=ctx.user, points=modal.points, reason=modal.reason, no_interaction=True)
        try:
            await ctx.edit_original_response(view=None)
        except:
            await ctx.message.delete()

    @ui.button(label='Ban', style=discord.ButtonStyle.danger)
    async def ban(self, ctx: discord.Interaction, button: ui.Button) -> None:
        modal = ReasonModal(bot=self.bot, ctx=ctx, author=ctx.user, title=f"Ban reason for {self.member}")
        await ctx.response.send_modal(modal)
        await modal.wait()

        await self.member.ban(reason=modal.reason)
        try:
            await ctx.edit_original_response(view=None)
        except:
            await ctx.message.delete()
