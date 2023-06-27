import discord
import discord.ui as ui

from utils.mod import warn
from utils.modals import AutoModWarnButtonModal, ReasonModal
from utils.services import user_service
from utils.config import cfg


class AutoModReportView(ui.View):
    member: discord.Member
    bot: discord.BotIntegration

    def __init__(self, member: discord.Member, bot: discord.BotIntegration) -> None:
        super().__init__()
        self.member = member
        self.bot = bot

        if not self.member.is_timed_out():
            self.remove_item(self.unmute)

    @ui.button(label='Dismiss', style=discord.ButtonStyle.green)
    async def dismiss(self, ctx: discord.Interaction, button: ui.Button) -> None:
        await ctx.message.delete()
        await ctx.response.defer()

    @ui.button(label='Warn', style=discord.ButtonStyle.red)
    async def warn(self, ctx: discord.Interaction, button: ui.Button) -> None:
        modal = AutoModWarnButtonModal(bot=self.bot, ctx=ctx, author=ctx.user, user=self.member)
        await ctx.response.send_modal(modal)
        await modal.wait()

        self.warn.disabled = True
        await warn(ctx, target_member=self.member, mod=ctx.user, points=modal.points, reason=modal.reason, no_interaction=True)
        try:
            await ctx.edit_original_response(view=self)
        except:
            await ctx.message.delete()

    @ui.button(label='Ban', style=discord.ButtonStyle.danger)
    async def ban(self, ctx: discord.Interaction, button: ui.Button) -> None:
        modal = ReasonModal(bot=self.bot, ctx=ctx, author=ctx.user, title=f"Ban reason for {self.member}")
        await ctx.response.send_modal(modal)
        await modal.wait()

        self.ban.disabled = True
        await self.member.ban(reason=modal.reason)
        try:
            await ctx.edit_original_response(view=self)
        except:
            await ctx.message.delete()

    @ui.button(label="Unmute", style=discord.ButtonStyle.gray)
    async def unmute(self, ctx: discord.Interaction, button: ui.Button) -> None:
        await self.member.timeout(None, reason="Action reviewed by a moderator")

        self.unmute.disabled = True
        await ctx.response.defer()
        try:
            await ctx.edit_original_response(view=self)
        except:
            await ctx.message.delete()

class AppealView(discord.ui.View):
    def __init__(self, bot: discord.Client, appealer: discord.User):
        super().__init__(timeout=None)
        self.bot = bot
        self.appealer = appealer
        self.replied = False

    @discord.ui.button(label='Accept Appeal', style=discord.ButtonStyle.green, custom_id='appealview:accept')
    async def accept_appeal(self, ctx: discord.Interaction, button: discord.ui.Button):
        modal = ReasonModal(bot=self.bot, ctx=ctx, author=ctx.user, title=f"Are you sure you want to accept this appeal?")
        await ctx.response.send_modal(modal)
        await modal.wait()
        if modal.reason is not None:
            user = user_service.get_user(self.appealer.id)
            user.is_appealing = False
            user.is_banned = False
            user.appeal_btn_msg_id = None
            guild = self.bot.get_guild(cfg.guild_id)
            await guild.unban(self.appealer, reason=modal.reason)
            try:
                await self.appealer.send(f"Your ban appeal for {guild.name} was accepted with the following reason: ```{modal.reason}```")
            except:
                pass
            user.save()
            await ctx.channel.send(f"{ctx.user.mention} accepted the appeal with the following reason: ```{modal.reason}```")
            await ctx.message.edit(embed=ctx.message.embeds[0], view=None)

    @discord.ui.button(label='Reject Appeal', style=discord.ButtonStyle.red, custom_id='appealview:reject')
    async def reject_appeal(self, ctx: discord.Interaction, button: discord.ui.Button):
        modal = ReasonModal(bot=self.bot, ctx=ctx, author=ctx.user, title=f"Are you sure you want to reject this appeal?")
        await ctx.response.send_modal(modal)
        await modal.wait()

        if modal.reason is not None:
            user = user_service.get_user(self.appealer.id)
            user.is_appealing = False
            user.appeal_btn_msg_id = None
            guild = self.bot.get_guild(cfg.guild_id)
            try:
                await self.appealer.send(f"Your ban appeal for {guild.name} was rejected with the following reason: ```{modal.reason}```")
            except:
                pass
            user.save()
            await ctx.channel.send(f"{ctx.user.mention} rejected the appeal with the following reason: ```{modal.reason}```")
            await ctx.message.edit(embed=ctx.message.embeds[0], view=None)

