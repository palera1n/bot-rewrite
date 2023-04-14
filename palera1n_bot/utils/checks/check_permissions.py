import discord
from discord.ext import commands
import os
from datamodels import PermissionLevel
from model import Guild
from utils.database.guild_service import GuildService

# TODO: finish check_permissions

guild_id = os.getenv("GUILD_ID")
owner_id = os.getenv("OWNER_ID")
the_guild = GuildService.get_guild()


async def check_permissions(ctx: discord.ApplicationContext, level: PermissionLevel) -> bool:
    _role_permission_mapping = {
        PermissionLevel.MEMPLUS: the_guild.role_memberplus,
        PermissionLevel.MEMPRO: the_guild.role_memberpro,
        PermissionLevel.HELPER: the_guild.role_genius,
        PermissionLevel.MOD: the_guild.role_moderator,
        PermissionLevel.ADMIN: the_guild.role_administrator,
    }
    if level == PermissionLevel.OWNER:
        return ctx.author.id == owner_id
    if check_permissions(ctx, level + 1) or (guild_id == ctx.guild.id and getattr(the_guild, f"role_{_role_permission_mapping[level]}")):
        return True
