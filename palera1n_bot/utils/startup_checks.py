import utils.database.guild_service as GuildService
from model import Guild
import os

the_guild: Guild = GuildService.get_guild()

roles_to_check = [
    "role_memberplus",
    "role_memberpro",
    "role_genius",
    "role_moderator",
    "role_administrator",
]


def check_envvars():
    if os.getenv("GUILD_ID") is None:
        raise AttributeError(
            "Database is not set up properly! The GUILD_ID environment variable is missing. Please recheck your variables.")
    if os.getenv("OWNER_ID") is None:
        raise AttributeError(
            "Database is not set up properly! The OWNER_ID environment variable is missing. Please recheck your variables.")
    if os.getenv("TOKEN") is None:
        raise AttributeError(
            "Database is not set up properly! The TOKEN environment variable is missing. Please recheck your variables.")


def check_perm_roles():
    for role in roles_to_check:
        try:
            getattr(the_guild, role)
        except AttributeError:
            raise AttributeError(
                f"Database is not set up properly! Role '{role}' is missing. Please run the setup.py command from GIR Rewrite.")


checks = [check_envvars, check_perm_roles]
