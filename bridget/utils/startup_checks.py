import os

from model import Guild
import utils.services.guild_service as GuildService


def check_envvars():
    if os.getenv("GUILD_ID") is None:
        raise AttributeError(
            "Database is not set up properly! The GUILD_ID environment variable is missing. Please recheck your variables."
        )

    if os.getenv("OWNER_ID") is None:
        raise AttributeError(
            "Database is not set up properly! The OWNER_ID environment variable is missing. Please recheck your variables."
        )

    if os.getenv("TOKEN") is None:
        raise AttributeError(
            "Database is not set up properly! The TOKEN environment variable is missing. Please recheck your variables."
        )


def check_perm_roles():
    the_guild: Guild = GuildService.get_guild()

    roles_to_check = [
        "role_memberplus",
        "role_memberpro",
        "role_helper",
        "role_moderator",
        "role_administrator",
    ]

    for role in roles_to_check:
        try:
            getattr(the_guild, role)
        except AttributeError:
            raise AttributeError(
                f"Database is not set up properly! Role '{role}' is missing. Please run `pdm run setup`."
            )


checks = [check_envvars, check_perm_roles]
