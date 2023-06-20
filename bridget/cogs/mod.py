import discord

from datetime import datetime
from discord import app_commands
from discord.utils import escape_markdown, escape_mentions

from utils import Cog, send_error, send_success, get_warnpoints
from utils.autocomplete import warn_autocomplete
from utils.mod import warn, prepare_liftwarn_log, notify_user, submit_public_log
from utils.services import guild_service, user_service
from utils.enums import PermissionLevel
from model.infraction import Infraction


class Mod(Cog):
    @PermissionLevel.MOD
    @app_commands.command()
    async def warn(self, ctx: discord.Interaction, user: discord.User, points: app_commands.Range[int, 1, 10], reason: str) -> None:
        """Warn a user

        Args:
            ctx (discord.ctx): Context
            user (discord.Member): User to warn
            points (app_commands.Range[int, 1, 10]): Points to give
            reason (str): Reason to warn
        """

        if user.top_role >= ctx.user.top_role:
            await send_error(ctx, "You can't warn this member.")
            return

        await ctx.response.defer()
        await warn(ctx, target_member=user, mod=ctx.user, points=points, reason=reason)

    @PermissionLevel.MOD
    @app_commands.autocomplete(infraction_id=warn_autocomplete)
    @app_commands.command()
    async def liftwarn(self, ctx: discord.Interaction, user: discord.User, infraction_id: str, reason: str) -> None:
        """Lift a user's warn

        Args:
            ctx (discord.Interaction): Context
            user (discord.Member): User to lift warn
            infraction_id (str): Id of the warn's infraction
            reason (str): Reason to lift warn
        """

        infractions = user_service.get_infractions(user.id)
        infraction = infractions.infractions.filter(_id=infraction_id).first()

        reason = escape_markdown(reason)
        reason = escape_mentions(reason)

        # sanity checks
        if infraction is None:
            await send_error(ctx, f"{user} has no infraction with ID {infraction_id}")
            return
        elif infraction._type != "WARN":
            await send_error(ctx, f"{user}'s infraction with ID {infraction_id} is not a warn infraction.")
            return
        elif infraction.lifted:
            await send_error(ctx, f"Infraction with ID {infraction_id} already lifted.")
            return

        u = user_service.get_user(id=user.id)
        if get_warnpoints(u) - int(infraction.punishment) < 0:
            await send_error(ctx, f"Can't lift Infraction #{infraction_id} because it would make {user.mention}'s points negative.")
            return

        # passed sanity checks, so update the infraction in DB
        infraction.lifted = True
        infraction.lifted_reason = reason
        infraction.lifted_by_tag = str(ctx.user)
        infraction.lifted_by_id = ctx.user.id
        infraction.lifted_date = datetime.now()
        infractions.save()

        # remove the warn points from the user in DB
        user_service.inc_points(user.id, -1 * int(infraction.punishment))
        dmed = True
        # prepare log embed, send to #public-logs, user, channel where invoked
        log = prepare_liftwarn_log(ctx.user, user, infraction)
        dmed = await notify_user(user, f"Your warn has been lifted in {ctx.guild}.", log)

        await send_success(ctx, embed=log, delete_after=10, ephemeral=False)
        await submit_public_log(ctx, guild_service.get_guild(), user, log, dmed)

    @PermissionLevel.ADMIN
    @app_commands.command()
    async def transferprofile(self, ctx: discord.Interaction, old_member: discord.Member, new_member: discord.Member) -> None:
        """Transfers all data in the database between users

        Args:
            ctx (discord.ctx): Context
            old_member (discord.Member): The user to transfer data from
            new_member (discord.Member): The user to transfer data to
        """

        u, infraction_count = user_service.transfer_profile(old_member.id, new_member.id)

        embed = discord.Embed(title="Transferred profile")
        embed.description = f"Transferred {old_member.mention}'s profile to {new_member.mention}"
        embed.color = discord.Color.blurple()
        embed.add_field(name="Level", value=u.level)
        embed.add_field(name="XP", value=u.xp)
        embed.add_field(name="Warn points", value=u.warn_points)
        embed.add_field(name="Infractions", value=infraction_count)

        await send_success(ctx, embed=embed, delete_after=10)
        try:
            await new_member.send(f"{ctx.user} has transferred your profile from {old_member}", embed=embed)
        except:
            pass

    @PermissionLevel.GUILD_OWNER
    @app_commands.command()
    async def clem(self, ctx: discord.Interaction, member: discord.Member) -> None:
        """Sets user's XP and Level to 0, freezes XP, sets warn points to 9

        Args:
            ctx (discord.ctx): Context
            member (discord.Member): The user to reset
        """

        if member.id == ctx.user.id:
            await send_error(ctx, "You can't call that on yourself.")
            return

        if member.id == self.bot.user.id:
            await send_error(ctx, "You can't call that on me :(")
            return

        results = user_service.get_user(member.id)

        if results.is_clem:
            await send_error(ctx, "That user is already on clem.")
            return

        results.is_clem = True
        results.is_xp_frozen = True
        results.save()

        infraction = Infraction(
            _id=guild_service.get_guild().infraction_id,
            _type="CLEM",
            mod_id=ctx.user.id,
            mod_tag=str(ctx.user),
            punishment=str(-1),
            reason="No reason."
        )

        # incrememnt DB's max infraction ID for next infraction
        guild_service.inc_infractionid()
        # add infraction to db
        user_service.add_infraction(member.id, infraction)

        await send_success(ctx, f"{member.mention} was put on clem.")

    @PermissionLevel.GUILD_OWNER
    @app_commands.command()
    async def unclem(self, ctx: discord.Interaction, member: discord.Member) -> None:
        """Removes the clem status, unfreezes XP, sets warn points back to before clem

        Args:
            ctx (discord.ctx): Context
            member (discord.Member): The user to unclem
        """

        if member.id == ctx.user.id:
            await send_error(ctx, "You can't call that on yourself.")
            return

        if member.id == self.bot.user.id:
            await send_error(ctx, "You can't call that on me :(")
            return

        results = user_service.get_user(member.id)


        if not results.is_clem:
            await send_error(ctx, "That user is not on clem.")
            return

        results.is_clem = False
        results.is_xp_frozen = False
        results.save()

        infraction = Infraction(
            _id=guild_service.get_guild().infraction_id,
            _type="UNCLEM",
            mod_id=ctx.user.id,
            mod_tag=str(ctx.user),
            punishment=str(-1),
            reason="No reason."
        )

        # incrememnt DB's max infraction ID for next infraction
        guild_service.inc_infractionid()
        # add infraction to db
        user_service.add_infraction(member.id, infraction)

        await send_success(ctx, f"{member.mention}'s clem has been lifted.")

