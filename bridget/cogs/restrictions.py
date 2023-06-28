import discord

from discord import app_commands

from utils import Cog, send_error, send_success
from utils.enums import PermissionLevel, RestrictionType
from utils.services import guild_service


class Restrictions(Cog):
    @PermissionLevel.MOD
    @app_commands.command()
    async def restrict(self, ctx: discord.Interaction, user: discord.Member, type: RestrictionType) -> None:
        """Restricts a user

        Args:
            ctx (discord.ctx): Context
            user (discord.Member): User to restrict
            type (RestrictionType): What to restrict
        """

        if user.top_role >= ctx.user.top_role:
            await send_error(ctx, "You can't restrict this member.")
            return

        try:
            role = ctx.guild.get_role(guild_service.get_guild()[str(type)])
            await user.add_roles(role, reason="restricted")
            await send_success(ctx, "User restricted successfully", ephemeral=True)
        except:
            await send_error(ctx, "Restriction role not found")


    @PermissionLevel.MOD
    @app_commands.command()
    async def unrestrict(self, ctx: discord.Interaction, user: discord.Member, type: RestrictionType) -> None:
        """Unrestricts a user

        Args:
            ctx (discord.ctx): Context
            user (discord.Member): User to unrestrict
            type (RestrictionType): What to unrestrict
        """

        if user.top_role >= ctx.user.top_role:
            await send_error(ctx, "You can't unrestrict this member.")
            return

        try:
            role = ctx.guild.get_role(guild_service.get_guild()[str(type)])
            await user.remove_roles(role, reason="unrestricted")
            await send_success(ctx, "User unrestricted successfully", ephemeral=True)
        except:
            await send_error(ctx, "Restriction role not found")

