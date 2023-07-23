from datetime import datetime
import io
import discord
import pytimeparse
import asyncio

from typing import Union
from enum import Enum
from discord import ui
from bridget.utils.enums import PermissionLevel
from bridget.utils.utils import send_error, send_success

from utils.services import user_service
from utils.services import guild_service
from utils.mod import warn
from .report_action import ModAction, ReportActionReason


class GenericDescriptionModal(discord.ui.Modal):
    def __init__(self, ctx: discord.Interaction, author: discord.Member, title: str, label: str = "Description", placeholder: str = "Please enter a description", prefill: str = ""):
        self.ctx = ctx
        self.author = author
        self.value = None

        super().__init__(title=title)

        self.add_item(
            discord.ui.TextInput(
                label=label,
                placeholder=placeholder,
                style=discord.TextStyle.long,
                default=prefill
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return

        self.ctx = interaction
        self.value = self.children[0].value

        self.stop()


async def report(bot: discord.Client, message: discord.Message, word: str, invite=None, image=None):
    """Deals with a report

    Parameters
    ----------
    bot : discord.Client
        "Bot object"
    message : discord.Message
        "Filtered message"
    word : str
        "Filtered word"
    invite : bool
        "Was the filtered word an invite?"

    """
    db_guild = guild_service.get_guild()
    channel = message.guild.get_channel(db_guild.channel_reports)

    ping_string = prepare_ping_string(db_guild, message)
    view = ReportActions(target_member=message.author)

    if invite:
        embed = prepare_embed(message, word, title="Invite filter")
        await channel.send(f"{ping_string}\nMessage contained invite: {invite}", embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True))
    elif image is not None:
        embed = prepare_embed(message, word, title="Image filter")
        await channel.send(f"{ping_string}\nMessage contained image with filtered text", embed=embed, view=view, file=discord.File(io.BytesIO(image), filename="filtered_image.png"), allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True))
    else:
        embed = prepare_embed(message, word)
        await channel.send(ping_string, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True))


async def manual_report(mod: discord.Member, target: Union[discord.Message, discord.Member] = None):
    """Deals with a report

    Parameters
    ----------
    bot : discord.Client
        "Bot object"
    message : discord.Message
        "Filtered message"
    mod : discord.Member
        "The moderator that started this report

    """
    db_guild = guild_service.get_guild()
    channel = target.guild.get_channel(db_guild.channel_reports)

    ping_string = f"{mod.mention} reported a member"
    if isinstance(target, discord.Message):
        view = ReportActions(target.author)
    else:
        view = ReportActions(target)

    embed = prepare_embed(target, title="A moderator reported a member")
    await channel.send(ping_string, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True))

async def report_raid_phrase(bot: discord.Client, message: discord.Message, domain: str):
    """Deals with a report

    Parameters
    ----------
    bot : discord.Client
        "Bot object"
    message : discord.Message
        "Filtered message"
    word : str
        "Filtered word"
    invite : bool
        "Was the filtered word an invite?"

    """
    db_guild = guild_service.get_guild()
    channel = message.guild.get_channel(db_guild.channel_reports)

    ping_string = prepare_ping_string(db_guild, message)
    view = RaidPhraseReportActions(message.author, domain)

    embed = prepare_embed(
        message, domain, title=f"Possible new raid phrase detected\n{domain}")
    await channel.send(ping_string, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True))


async def report_spam(bot, msg, user, title):
    db_guild = guild_service.get_guild()
    channel = msg.guild.get_channel(db_guild.channel_reports)
    ping_string = prepare_ping_string(db_guild, msg)

    view = SpamReportActions(user)
    embed = prepare_embed(msg, title=title)

    await channel.send(ping_string, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True))


async def report_raid(user, msg=None):
    embed = discord.Embed()
    embed.title = "Possible raid occurring"
    embed.description = "The raid filter has been triggered 5 or more times in the past 10 seconds. I am automatically locking all the channels. Use `/unfreeze` when you're done."
    embed.color = discord.Color.red()
    embed.set_thumbnail(url=user.display_avatar)
    embed.add_field(name="Member", value=f"{user} ({user.mention})")
    if msg is not None:
        embed.add_field(name="Message", value=msg.content, inline=False)

    db_guild = guild_service.get_guild()
    reports_channel = user.guild.get_channel(db_guild.channel_reports)
    await reports_channel.send(f"<@&{db_guild.role_moderator}>", embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))


def prepare_ping_string(db_guild, message):
    """Prepares modping string

    Parameters
    ----------
    db_guild
        "Guild DB"
    message : discord.Message
        "Message object"

    """
    """ping_string = ""
    if cfg.dev:
        return ping_string

    role = message.guild.get_role(db_guild.role_moderator)
    for member in role.members:
        offline_ping = (user_service.get_user(member.id)).offline_report_ping
        if member.status == discord.Status.online or offline_ping:
            ping_string += f"{member.mention} "

    return ping_string"""
    return f"<@&{guild_service.get_guild().role_reportping}> "

def prepare_embed(target: Union[discord.Message, discord.Member], word: str = None, title="Word filter"):
    """Prepares embed

    Parameters
    ----------
    message : discord.Message
        "Message object"
    word : str
        "Filtered word"
    title : str
        "Embed title"

    """
    if isinstance(target, discord.Message):
        member = target.author
    else:
        member = target

    user_info = user_service.get_user(member.id)
    rd = user_service.rundown(member.id)
    rd_text = ""
    for r in rd:
        if r._type == "WARN":
            r.punishment += " points"
        rd_text += f"**{r._type}** - {r.punishment} - {r.reason} - {discord.utils.format_dt(r.date, style='R')}\n"

    embed = discord.Embed(title=title)
    embed.color = discord.Color.red()

    embed.set_thumbnail(url=member.display_avatar)
    embed.add_field(name="Member", value=f"{member} ({member.mention})")
    if isinstance(target, discord.Message):
        embed.add_field(name="Channel", value=target.channel.mention)

        if len(target.content) > 400:
            target.content = target.content[0:400] + "..."

    if word is not None:
        embed.add_field(name="Message", value=discord.utils.escape_markdown(
            target.content) + f"\n\n[Link to message]({target.jump_url}) | Filtered word: **{word}**", inline=False)
    else:
        if isinstance(target, discord.Message):
            embed.add_field(name="Message", value=discord.utils.escape_markdown(
                target.content) + f"\n\n[Link to message]({target.jump_url})", inline=False)
    embed.add_field(
        name="Join date", value=f"{discord.utils.format_dt(member.joined_at, style='F')} ({discord.utils.format_dt(member.joined_at, style='R')})", inline=True)
    embed.add_field(name="Created",
                    value=f"{discord.utils.format_dt(member.created_at, style='F')} ({discord.utils.format_dt(member.created_at, style='R')})", inline=True)

    embed.add_field(name="Warn points",
                    value=user_info.warn_points, inline=True)
    account_age = (datetime.now() - datetime.fromtimestamp(discord.utils.snowflake_time(member.id))).days

    if member.joined_at != None:
        guild_age = (datetime.now() - member.joined_at).days
    else: 
        guild_age = account_age

    risk_factor = user_service.get_user(member.id).warn_points * 0.5 + min(len(user_service.get_infractions(member.id)), 10) * 0.3 + min((guild_age / 30), 10) * 0.1 + min(account_age / 60, 10) * 0.1

    embed.add_field(name="User risk factor (scale: 1-10)",
                    value=f"{risk_factor} (warn points * 0.5 + infraction count (max 10) * 0.3 + days since guild join / 30 (max 10) * 0.1 + days since account creation / 60 (max 10) * 0.1)"
                    )

    reversed_roles = member.roles
    reversed_roles.reverse()

    roles = ""
    for role in reversed_roles[0:4]:
        if role != member.guild.default_role:
            roles += role.mention + " "
    roles = roles.strip() + "..."

    embed.add_field(
        name="Roles", value=roles if roles else "None", inline=False)

    if len(rd) > 0:
        embed.add_field(name=f"{len(rd)} most recent cases",
                        value=rd_text, inline=True)
    else:
        embed.add_field(name=f"Recent cases",
                        value="This user has no cases.", inline=True)
    return embed

class ReportActions(ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=None)
        self.target_member = target_member

    async def interaction_check(self, interaction: discord.Interaction):
        if not PermissionLevel.MEMPLUS == interaction.user:
            return False
        return True

    @ui.button(emoji="✅", label="Dismiss", style=discord.ButtonStyle.primary)
    async def dismiss(self, interaction: discord.Interaction, _: ui.Button):
        if not PermissionLevel.MOD == interaction.user:
            raise PermissionError(
                "You do not have permission to use this command.")
        await interaction.message.delete()
        self.stop()

    @ui.button(emoji="⚠️", label="Warn", style=discord.ButtonStyle.primary)
    async def warn(self, interaction: discord.Interaction, _: ui.Button):
        if not PermissionLevel.MOD == interaction.user:
            raise PermissionError(
                "You do not have permission to use this command.")

        view = ReportActionReason(
            target_member=self.target_member, mod=interaction.user, mod_action=ModAction.WARN)
        await interaction.response.send_message(embed=discord.Embed(description=f"{interaction.user.mention}, choose a warn reason for {self.target_member.mention}.", color=discord.Color.blurple()), view=view)
        await view.wait()
        if view.success:
            await interaction.message.delete()
            self.stop()
        else:
            await interaction.delete_original_message()

    @ui.button(emoji="❌", label="Ban", style=discord.ButtonStyle.primary)
    async def ban(self, interaction: discord.Interaction, _: ui.Button):
        if not PermissionLevel.MOD == interaction.user:
            raise PermissionError(
                "You do not have permission to use this command.")

        view = ReportActionReason(
            target_member=self.target_member, mod=interaction.user, mod_action=ModAction.BAN)
        await interaction.response.send_message(embed=discord.Embed(description=f"{interaction.user.mention}, choose a ban reason for {self.target_member.mention}.", color=discord.Color.blurple()), view=view)
        await view.wait()
        if view.success:
            await interaction.message.delete()
        else:
            await interaction.delete_original_message()
        self.stop()

    @ui.button(emoji="🆔", label="Post ID", style=discord.ButtonStyle.primary)
    async def id(self, interaction: discord.Interaction, _: ui.Button):
        if not PermissionLevel.MOD == interaction.user:
            raise PermissionError(
                "You do not have permission to use this command.")

        await interaction.response.send_message(self.target_member.id)
        await asyncio.sleep(10)
        await interaction.delete_original_message()

    @ui.button(emoji="🧹", label="Clean up", style=discord.ButtonStyle.primary)
    async def purge(self, interaction: discord.Interaction, button: ui.Button):
        if not PermissionLevel.MOD == interaction.user:
            raise PermissionError(
                "You do not have permission to use this command.")

        await interaction.channel.purge(limit=100)
        self.stop()

    @ui.button(emoji="🔎", label="Claim report", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        if not PermissionLevel.MOD == interaction.user:
            raise PermissionError(
                "You do not have permission to use this command.")

        report_embed = interaction.message.embeds[0]
        if "(claimed)" in report_embed.title:
            await send_error(f"{interaction.user.mention}, this report has already been claimed.", whisper=True)
            return

        embed = discord.Embed(color=discord.Color.blurple())
        embed.description = f"{interaction.user.mention} is looking into {self.target_member.mention}'s report!"
        await interaction.response.send_message(embed=embed)
        report_embed.color = discord.Color.orange()

        report_embed.title = f"{report_embed.title} (claimed)"
        await interaction.message.edit(embed=report_embed)

        await asyncio.sleep(10)
        await interaction.delete_original_message()


class RaidPhraseReportActions(ui.View):
    def __init__(self, author: discord.Member, domain: str):
        super().__init__(timeout=None)
        self.target_member = author
        self.domain = domain

    async def interaction_check(self, interaction: discord.Interaction):
        if not PermissionLevel.MOD == interaction.user:
            return False
        return True

    @ui.button(emoji="✅", label="Dismiss", style=discord.ButtonStyle.primary)
    async def dismiss(self, interaction: discord.Interaction, button: ui.Button):
        try:
            # await unmute(interaction, self.target_member, mod=interaction.user, reason="Reviewed by a moderator.")
            await self.target_member.edit(timed_out_until=datetime.now())
        except Exception:
            await send_error("I wasn't able to unmute them.", delete_after=5)
        finally:
            await interaction.message.delete()
            self.stop()

    @ui.button(emoji="💀", label="Ban and add raidphrase", style=discord.ButtonStyle.primary)
    async def ban(self, interaction: discord.Interaction, button: ui.Button):
        try:
            # await ban(interaction, self.target_member, mod=interaction.user, reason="Raid phrase detected")
            self.target_member.ban(delete_message_days=1, reason="Raid phrase detected")
        except Exception:
            await send_error("I wasn't able to ban them.", delete_after=5)

        done = guild_service.add_raid_phrase(self.domain)
        if done:
            await send_success(f"{self.domain} was added to the raid phrase list.", delete_after=5)
        else:
            await send_error(f"{self.domain} was already in the raid phrase list.", delete_after=5)

        await interaction.message.delete()
        self.stop()


class SpamReportActions(ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=None)
        self.target_member = author

    async def interaction_check(self, interaction: discord.Interaction):
        if not PermissionLevel.MOD == interaction.user:
            return False
        return True

    @ui.button(emoji="✅", label="Dismiss", style=discord.ButtonStyle.primary)
    async def dismiss(self, interaction: discord.Interaction, _: ui.Button):
        try:
            # await unmute(interaction, self.target_member, interaction.guild.me, reason="Reviewed by a moderator.")
            await self.target_member.edit(timed_out_until=datetime.now(), reason="Reviewed by a moderator.")
        except Exception:
            await send_error("I wasn't able to unmute them.", delete_after=5)
        finally:
            await interaction.message.delete()
            self.stop()

    @ui.button(emoji="💀", label="Ban", style=discord.ButtonStyle.primary)
    async def ban(self, interaction: discord.Interaction, _: ui.Button):
        try:
            # await ban(interaction, self.target_member, mod=interaction.user, reason="Spam detected")
            self.target_member.ban(reason="Spam detected")
        except Exception:
            await send_error("I wasn't able to ban them.")
        finally:
            await interaction.message.delete()
            self.stop()

    # @ui.button(emoji="⚠️", label="Temporary mute", style=discord.ButtonStyle.primary)
    # async def mute(self, interaction: discord.Interaction, button: ui.Button):
    #     view = GenericDescriptionModal(
    #         ctx, interaction.user, title=f"Mute duration for {self.target_member}", label="How long should they be muted for?", placeholder="i.e 1h, 1d, ...")
    #     await interaction.response.send_modal(view)
    #     await view.wait()
    #     if view.value is not None:
    #         try:
    #             duration = pytimeparse.parse(view.value)
    #         except ValueError:
    #             await send_error("I couldn't parse that duration.")

    #         await self.target_member.edit(timed_out_until=None)
    #         # await mute(ctx, self.target_member, mod=interaction.user, dur_seconds=duration, reason="A moderator has reviewed your spam report.")
    #         await self.target_member.timed_out_until()
    #         await interaction.message.delete()
    #         self.stop()
