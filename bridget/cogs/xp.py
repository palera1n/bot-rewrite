import discord
import math

from discord.ext import commands
from discord import app_commands
from random import randint
from typing import List

from utils.services import guild_service
from utils.services import user_service
from utils.config import cfg
from utils.enums import PermissionLevel
from utils.menus import Menu
from model import Guild


def format_xptop_page(ctx: discord.Interaction, entries, current_page: int, all_pages) -> discord.Embed:
    """Formats the page for the xptop embed.

    Parameters
    ----------
    entry : dict
        "The dictionary for the entry"
    all_pages : list
        "All entries that we will eventually iterate through"
    current_page : number
        "The number of the page that we are currently on" 

    Returns
    -------
    discord.Embed
        "The embed that we will send"

    """
    embed = discord.Embed(title=f'Leaderboard', color=discord.Color.blurple())
    for i, user in entries:
        member = ctx.guild.get_member(user._id)
        trophy = ''
        if current_page == 1:
            if i == entries[0][0]:
                trophy = ':first_place:'
                embed.set_thumbnail(url=member.avatar)
            if i == entries[1][0]:
                trophy = ':second_place:'
            if i == entries[2][0]:
                trophy = ':third_place:'

        embed.add_field(name=f"#{i+1} - Level {user.level}",
                        value=f"{trophy} {member.mention}", inline=False)

    embed.set_footer(text=f"Page {current_page} of {len(all_pages)}")
    return embed


class Xp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def xp(self, ctx: discord.Interaction, member: discord.Member = None) -> None:
        """Show your or another user's XP

        Args:
            ctx (discord.ctx): Context
            member (discord.Member, optional): Member to get XP of
        """

        if member is None:
            member = ctx.user

        results = user_service.get_user(member.id)

        whisper = False
        bot_chan = guild_service.get_guild().channel_botspam
        if not PermissionLevel.MOD.check(ctx) and ctx.channel_id != bot_chan:
            whisper = True

        embed = discord.Embed(title="Level Statistics")
        embed.color = member.top_role.color
        embed.set_author(name=member, icon_url=member.display_avatar)
        embed.add_field(
            name="Level", value=results.level if not results.is_clem else "0", inline=True)
        embed.add_field(
            name="XP", value=f'{results.xp}/{self.xp_for_next_level(results.level)}' if not results.is_clem else "0/0", inline=True)
        rank, overall = user_service.leaderboard_rank(results.xp)
        embed.add_field(
            name="Rank", value=f"{rank}/{overall}" if not results.is_clem else f"{overall}/{overall}", inline=True)

        await ctx.response.send_message(embed=embed, ephemeral=whisper)

    @app_commands.command()
    async def xptop(self, ctx: discord.Interaction) -> None:
        """Show the XP leaderboard.

        Args:
            ctx (discord.ctx): Context
        """

        whisper = False
        bot_chan = guild_service.get_guild().channel_botspam
        if not PermissionLevel.MOD.check(ctx) and ctx.channel_id != bot_chan:
            whisper = True

        results = enumerate(user_service.leaderboard())
        results = [(i, m) for (i, m) in results if ctx.guild.get_member(
            m._id) is not None][0:100]

        menu = Menu(ctx, results, per_page=10,
                    page_formatter=format_xptop_page, whisper=whisper)
        await menu.start()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot:
            return
        if member.guild.id != cfg.guild_id:
            return

        user = user_service.get_user(id=member.id)

        if user.is_xp_frozen or user.is_clem:
            return

        level = user.level
        db_guild = guild_service.get_guild()

        roles_to_add = self.assess_new_roles(level, db_guild)
        await self.add_new_roles(member, roles_to_add)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild:
            return
        if message.guild.id != cfg.guild_id:
            return
        if message.author.bot:
            return

        db_guild = guild_service.get_guild()
        if message.channel.id == db_guild.channel_botspam:
            return

        user = user_service.get_user(id=message.author.id)
        if user.is_xp_frozen or user.is_clem:
            return

        xp_to_add = randint(0, 11)
        new_xp, level_before = user_service.inc_xp(
            message.author.id, xp_to_add)
        new_level = self.get_level(new_xp)

        if new_level > level_before:
            user_service.inc_level(message.author.id)

        roles_to_add = self.assess_new_roles(new_level, db_guild)
        await self.add_new_roles(message, roles_to_add)

    def assess_new_roles(self, new_level: int, db: Guild) -> List[int]:
        roles_to_add = []
        if 15 <= new_level:
            roles_to_add.append(db.role_memberplus)
        if 30 <= new_level:
            roles_to_add.append(db.role_memberpro)
        if 50 <= new_level:
            roles_to_add.append(db.role_memberedition)
        if 75 <= new_level:
            roles_to_add.append(db.role_memberone)
        if 100 <= new_level:
            roles_to_add.append(db.role_memberultra)

        return roles_to_add

    async def add_new_roles(self, obj: discord.Message | discord.User, roles_to_add: List[int]) -> None:
        if roles_to_add is None:
            return

        member = obj
        if isinstance(obj, discord.Message):
            member = obj.author

        roles_to_add = [member.guild.get_role(role) for role in roles_to_add if member.guild.get_role(
            role) is not None and member.guild.get_role(role) not in member.roles]
        await member.add_roles(*roles_to_add, reason="XP roles")

    def get_level(self, current_xp: int) -> int:
        level = 0
        xp = 0
        while xp <= current_xp:
            xp = xp + 45 * level * (math.floor(level / 10) + 1)
            level += 1
        return level

    def xp_for_next_level(self, _next: int) -> int:
        level = 0
        xp = 0

        for _ in range(0, _next):
            xp = xp + 45 * level * (math.floor(level / 10) + 1)
            level += 1

        return xp
