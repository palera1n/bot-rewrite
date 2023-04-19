import discord
import flag
import datetime
import pytz

from discord.ext import commands
from discord import app_commands
from typing import List

from utils import Cog, send_success
from utils.services import user_service


async def timezone_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [app_commands.Choice(name=tz, value=tz) for tz in pytz.common_timezones_set if current.lower(
    ) in tz.lower() or current.lower() in tz.replace("_", " ").lower()][:25]


@app_commands.guild_only()
class Timezones(Cog, commands.GroupCog, group_name="timezones"):
    timezone_country = {}
    for countrycode in pytz.country_timezones:
        timezones = pytz.country_timezones[countrycode]
        for timezone in timezones:
            timezone_country[timezone] = countrycode

    def country_code_to_emoji(self, country_code: str):
        try:
            return " " + flag.flag(country_code)
        except ValueError:
            return ""

    @app_commands.command()
    @app_commands.autocomplete(zone=timezone_autocomplete)
    async def set(self, ctx: discord.Interaction, zone: str) -> None:
        """Set your timezone so that others can view it

        Args:
            ctx (discord.Interaction): Context
            zone (str): The timezone to set
        """

        if zone not in pytz.common_timezones_set:
            raise commands.BadArgument("Timezone was not found!")

        db_user = user_service.get_user(ctx.user.id)
        db_user.timezone = zone
        db_user.save()

        await send_success(ctx, f"We set your timezone to `{zone}`! It can now be viewed with `/timezone view`.")

    @app_commands.command()
    async def remove(self, ctx: discord.Interaction) -> None:
        """Remove your timezone from the database

        Args:
            ctx (discord.Interaction): Context
        """

        db_user = user_service.get_user(ctx.user.id)
        db_user.timezone = None
        db_user.save()

        await send_success(ctx, "We have removed your timezone from the database.")

    @app_commands.command()
    @app_commands.describe(member="Member to view time of")
    async def view(self, ctx: discord.Interaction, member: discord.Member) -> None:
        """Get a timezone of an user

        Args:
            ctx (discord.Interaction): Context
            member (discord.Member): Member to view time of
        """

        db_user = user_service.get_user(member.id)
        if db_user.timezone is None:
            raise commands.BadArgument(
                f"{member.mention} has not set a timezone!")

        country_code = self.timezone_country.get(db_user.timezone)
        flaggy = ""
        if country_code is not None:
            flaggy = self.country_code_to_emoji(country_code)

        await send_success(ctx, f"{member.mention}'s timezone is `{db_user.timezone}` {flaggy}\nIt is currently `{datetime.datetime.now(pytz.timezone(db_user.timezone)).strftime('%I:%M %p %Z')}`", ephemeral=False)
