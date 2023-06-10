import discord

from discord import app_commands, Embed

from utils import Cog, send_error, send_success
from utils.autocomplete import rule_autocomplete
from utils.services import guild_service, user_service


class Misc(Cog):
    @app_commands.autocomplete(title=rule_autocomplete)
    @app_commands.command()
    async def rule(self, ctx: discord.Interaction, title: str) -> None:
        """Posts a rule

        Args:
            ctx (discord.ctx): Context
            title (str): The title of the rule
        """

        try:
            channel = ctx.guild.get_channel(guild_service.get_guild().channel_rules)
            msg = await channel.fetch_message(int(title))

            await send_success(ctx, embed=msg.embeds[0], ephemeral=False)
        except:
            await send_error(ctx, "Could not find rule")

    @app_commands.command()
    async def userinfo(self, ctx: discord.Interaction, user: discord.Member = None) -> None:
        """Get info about a user.

        Args:
            ctx (discord.ctx): Context
            user (discord.Member, optional): User to get info of
        """

        if not user:
            user = ctx.user
        usr = user_service.get_user(user.id)

        embed = Embed(title="User Information")
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
        embed.add_field(name="Username", value=f"{str(user)} ({user.mention})", inline=True)
        embed.add_field(name="Level", value=usr.level, inline=True)
        embed.add_field(name="XP", value=usr.xp, inline=True)

        roles = [r.mention for r in user.roles if r.name != "@everyone"]
        roles.reverse()
        embed.add_field(name="Roles", value=" ".join(roles), inline=False)

        embed.add_field(name="Join date", value=f"<t:{int(user.joined_at.timestamp())}> (<t:{int(user.joined_at.timestamp())}:R>)", inline=True)
        embed.add_field(name="Account creation date", value=f"<t:{int(user.created_at.timestamp())}> (<t:{int(user.created_at.timestamp())}:R>)", inline=True)

        await ctx.response.send_message(embed=embed)
