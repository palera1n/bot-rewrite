import discord

from datetime import datetime
from discord import app_commands
from discord.utils import escape_markdown, escape_mentions

from utils import Cog, send_error, send_success
from utils.autocomplete import warn_autocomplete
from utils.mod import warn, prepare_liftwarn_log, notify_user, submit_public_log
from utils.services import guild_service, user_service
from utils.enums import PermissionLevel


class Mod(Cog):
    @PermissionLevel.MOD
    @app_commands.command()
    async def warn(self, ctx: discord.Interaction, member: discord.Member, points: app_commands.Range[int, 1, 10], reason: str):
        """Warn a member

        Args:
            ctx (discord.ctx): Context
            member (discord.Member): Member to warn
            points (app_commands.Range[int, 1, 10]): Points to give
            reason (str): Reason to warn
        """

        if member.top_role >= ctx.user.top_role:
            await send_error(ctx, "You can't warn this member.")
            return

        await ctx.response.defer()
        await warn(ctx, target_member=member, mod=ctx.user, points=points, reason=reason)

    @PermissionLevel.MOD
    @app_commands.autocomplete(case_id=warn_autocomplete)
    @app_commands.command()
    async def liftwarn(self, ctx: discord.Interaction, member: discord.Member, case_id: str, reason: str) -> None:
        """Lift a member's warn

        Args:
            ctx (discord.Interaction): Context
            member (discord.Member): Member to lift warn
            case_id (str): Id of the warn's case
            reason (str): Reason to lift warn
        """

        cases = user_service.get_cases(member.id)
        case = cases.cases.filter(_id=case_id).first()

        reason = escape_markdown(reason)
        reason = escape_mentions(reason)

        # sanity checks
        if case is None:
            await send_error(ctx, f"{member} has no case with ID {case_id}")
            return
        elif case._type != "WARN":
            await send_error(ctx, f"{member}'s case with ID {case_id} is not a warn case.")
            return
        elif case.lifted:
            await send_error(ctx, f"Case with ID {case_id} already lifted.")
            return

        u = user_service.get_user(id=member.id)
        if u.warn_points - int(case.punishment) < 0:
            await send_error(ctx, f"Can't lift Case #{case_id} because it would make {member.mention}'s points negative.")
            return

        # passed sanity checks, so update the case in DB
        case.lifted = True
        case.lifted_reason = reason
        case.lifted_by_tag = str(ctx.user)
        case.lifted_by_id = ctx.user.id
        case.lifted_date = datetime.now()
        cases.save()

        # remove the warn points from the user in DB
        user_service.inc_points(member.id, -1 * int(case.punishment))
        dmed = True
        # prepare log embed, send to #public-logs, user, channel where invoked
        log = prepare_liftwarn_log(ctx.user, member, case)
        dmed = await notify_user(member, f"Your warn has been lifted in {ctx.guild}.", log)

        await send_success(ctx, embed=log, delete_after=10, ephemeral=False)
        await submit_public_log(ctx, guild_service.get_guild(), member, log, dmed)

    @warn.error
    @liftwarn.error
    async def error_handle(self, ctx: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.MissingPermissions):
            await send_error(ctx, "You are not allowed to use this command.")
            return
