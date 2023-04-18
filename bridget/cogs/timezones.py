from discord.ext import commands
import discord
from discord import app_commands
import flag
from utils.services import user_service
import datetime
from utils import send_success
from typing import List
import pytz
from utils import Cog

async def timezone_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [app_commands.Choice(name=tz, value=tz) for tz in pytz.common_timezones_set if current.lower() in tz.lower() or current.lower() in tz.replace("_", " ").lower()][:25]


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
    
    @app_commands.command(name="set", description="Set your timezone so that others can view it")
    @app_commands.describe(zone="The timezone to set")
    @app_commands.autocomplete(zone=timezone_autocomplete)
    async def _set(self, ctx: discord.Interaction, zone: str) -> None:
        if zone not in pytz.common_timezones_set:
            raise commands.BadArgument("Timezone was not found!")

        db_user = user_service.get_user(ctx.user.id)
        db_user.timezone = zone
        db_user.save()

        footer = None
        if self.timezone_country.get(zone) is None:
            footer = "Tip: this timezone is not a city. Pick a major city near you to show what country you're in! See /timezone list for more."

        await send_success(ctx, f"We set your timezone to `{zone}`! It can now be viewed with `/timezone view`.")


    @app_commands.command(name="remove", description="Remove your timezone from the database")
    async def remove(self, ctx: discord.Interaction) -> None:
        db_user = user_service.get_user(ctx.user.id)
        db_user.timezone = None
        db_user.save()

        await send_success(ctx, f"We have removed your timezone from the database.")
    
    @app_commands.command(name="view", description="Get a timezone of an user")
    @app_commands.describe(member="Member to view time of")
    async def timezones(self, ctx: discord.Interaction, member: discord.Member) -> None:
        db_user = user_service.get_user(member.id)
        if db_user.timezone is None:
            raise commands.BadArgument(f"{member.mention} has not set a timezone!")

        country_code = self.timezone_country.get(db_user.timezone)
        flaggy = ""
        if country_code is not None:
            flaggy = self.country_code_to_emoji(country_code)

        await send_success(ctx, f"{member.mention}'s timezone is `{db_user.timezone}` {flaggy}\nIt is currently `{datetime.datetime.now(pytz.timezone(db_user.timezone)).strftime('%I:%M %p %Z')}`", ephemeral=False)
