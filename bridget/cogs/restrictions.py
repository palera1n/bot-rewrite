import discord

from discord import PermissionOverwrite, app_commands

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

    @Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        if type(channel) == discord.TextChannel:
            role_channel = channel.guild.get_role(guild_service.get_guild().role_channelrestriction)
            role_media = channel.guild.get_role(guild_service.get_guild().role_mediarestriction)
            role_reaction = channel.guild.get_role(guild_service.get_guild().role_reactionrestriction)

            perm_channel = channel.overwrites_for(role_channel)
            perm_channel.view_channel = False

            perm_media = channel.overwrites_for(role_media)
            perm_media.embed_links = False
            perm_media.attach_files = False
            perm_media.external_emojis = False
            perm_media.external_stickers = False

            perm_reaction = channel.overwrites_for(role_reaction)
            perm_reaction.add_reactions = False

            await channel.set_permissions(role_channel, overwrite=perm_channel)
            await channel.set_permissions(role_media, overwrite=perm_media)
            await channel.set_permissions(role_reaction, overwrite=perm_reaction)

