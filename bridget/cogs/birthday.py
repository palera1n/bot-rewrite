import asyncio
import pytz
import discord

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord import app_commands
from bridget.utils.autocomplete import date_autocompleter
from bridget.utils.utils import Cog, send_success

from utils.services import guild_service, user_service
from utils.config import cfg
from utils.enums import PermissionLevel

MONTH_MAPPING = {
    "January": {
        "value": 1,
        "max_days": 31,
    },
    "February": {
        "value": 2,
        "max_days": 29,
    },
    "March": {
        "value": 3,
        "max_days": 31,
    },
    "April": {
        "value": 4,
        "max_days": 30,
    },
    "May": {
        "value": 5,
        "max_days": 31,
    },
    "June": {
        "value": 6,
        "max_days": 30,
    },
    "July": {
        "value": 7,
        "max_days": 31,
    },
    "August": {
        "value": 8,
        "max_days": 31,
    },
    "September": {
        "value": 9,
        "max_days": 30,
    },
    "October": {
        "value": 10,
        "max_days": 31,
    },
    "November": {
        "value": 11,
        "max_days": 30,
    },
    "December": {
        "value": 12,
        "max_days": 31,
    },
    
}

async def give_user_birthday_role(bot, db_guild, user, guild):
    birthday_role = guild.get_role(db_guild.role_birthday)
    if birthday_role is None:
        return

    if birthday_role in user.roles:
        return

    # calculate the different between now and tomorrow 12AM
    now = datetime.now(pytz.timezone('US/Eastern'))
    h = now.hour / 24
    m = now.minute / 60 / 24

    # schedule a task to remove birthday role (tomorrow) 12AM
    try:
        time = now + timedelta(days=1-h-m)
        bot.tasks.schedule_remove_bday(user.id, time)
    except Exception:
        return

    await user.add_roles(birthday_role)

    try:
        await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 24 hours.")
    except Exception:
        pass

class Birthday(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.eastern_timezone = pytz.timezone('US/Eastern')
        self.birthday.start()

    def cog_unload(self):
        self.birthday.cancel()

    @app_commands.choices(month=[app_commands.Choice(name=m, value=m) for m in MONTH_MAPPING.keys()])
    @app_commands.autocomplete(date=date_autocompleter)
    @app_commands.command()
    async def mybirthday(self, ctx: discord.Interaction, month: str, date: int) -> None:
        user = ctx.user
        if not (PermissionLevel.MEMPLUS == ctx.user or user.premium_since is not None):
            raise commands.BadArgument(
                "You need to be at least Member+ or a Nitro booster to use that command.")

        month = MONTH_MAPPING.get(month)
        if month is None:
            raise commands.BadArgument("You gave an invalid date")

        month = month["value"]

        # ensure date is real (2020 is a leap year in case the birthday is leap day)
        try:
            datetime(year=2020, month=month, day=date, hour=12)
        except ValueError:
            raise commands.BadArgument("You gave an invalid date.")

        # fetch user profile from DB
        db_user = user_service.get_user(user.id)

        # mods are able to ban users from using birthdays, let's handle that
        if db_user.birthday_excluded:
            raise commands.BadArgument("You are banned from birthdays.")

        # if the user already has a birthday set in the database, refuse to change it (if not a mod)
        if db_user.birthday != [] and not PermissionLevel.MOD == ctx.user:
            raise commands.BadArgument(
                "You already have a birthday set! You need to ask a mod to change it.")

        # passed all the sanity checks, let's save the birthday
        db_user.birthday = [month, date]
        db_user.save()

        await send_success(ctx, description=f"Your birthday was set.")
        # if it's the user's birthday today let's assign the role right now!
        today = datetime.today().astimezone(self.eastern_timezone)
        if today.month == month and today.day == date:
            db_guild = guild_service.get_guild()
            await give_user_birthday_role(self.bot, db_guild, ctx.user, ctx.guild)

    @tasks.loop(seconds=120)
    async def birthday(self):
        """Background task to scan database for users whose birthday it is today.
        If it's someone's birthday, the bot will assign them the birthday role for 24 hours."""

        # assign the role at 12am US Eastern time
        eastern = pytz.timezone('US/Eastern')
        today = datetime.today().astimezone(eastern)
        # the date we will check for in the database
        date = [today.month, today.day]
        # get list of users whose birthday it is today
        birthdays = user_service.retrieve_birthdays(date)

        guild = self.bot.get_guild(cfg.guild_id)
        if not guild:
            return

        db_guild = guild_service.get_guild()
        birthday_role = guild.get_role(db_guild.role_birthday)
        if not birthday_role:
            return

        # give each user whose birthday it is today the birthday role
        for person in birthdays:
            if person.birthday_excluded:
                continue

            user = guild.get_member(person._id)
            if user is None:
                return

            await give_user_birthday_role(self.bot, db_guild, user, guild)