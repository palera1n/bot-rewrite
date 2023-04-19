import discord

from enum import IntEnum, unique, auto

from .services import guild_service
from .config import cfg


@unique
class PermissionLevel(IntEnum):
    """Permission level enum"""

    EVERYONE = 0
    MEMPLUS = 1
    MEMPRO = 2
    HELPER = 3
    MOD = 4
    ADMIN = 5
    GUILD_OWNER = 6
    OWNER = 7

    # Checks
    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __str__(self):
        return {
                self.MEMPLUS: "role_memberplus",
                self.MEMPRO: "role_memberpro",
                self.HELPER: "role_helper",
                self.MOD: "role_moderator",
                self.ADMIN: "role_administrator",
        }[self] 

    def __eq__(self, other):
        if isinstance(other, discord.Member):
            if self == self.EVERYONE:
                return True
            if self == self.GUILD_OWNER:
                return other.guild.owner == other
            if self == self.OWNER:
                return other.id == cfg.owner_id

            return getattr(guild_service.get_guild(), str(self)) in list(map(lambda r: r.id, other.roles)) or self + 1 == other

        return self.value == other.value

    def __add__(self, other):
        return self.__class__(self.value + other)

    def check(self, ctx: discord.Interaction):
        if not self == ctx.user:
            raise discord.app_commands.MissingPermissions(
                "You don't have permission to use this command.")
        return True

    def __call__(self, command: discord.app_commands.Command):
        command.checks.append(self.check)
        return command

    def __hash__(self):
        return hash(self.value)
