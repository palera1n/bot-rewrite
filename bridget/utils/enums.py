import discord

from enum import IntEnum, unique
from discord.automod import AutoModRule
from typing import Any, List, Optional, Union

from .services import guild_service
from .config import cfg
from .errors import MissingPermissionsError


def rule_has_timeout(rule: AutoModRule) -> bool:
    for act in rule.actions:
        if act.type == discord.AutoModRuleActionType.timeout:
            return True
    return False

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
    def __lt__(self, other: int) -> bool:
        return self.value < other.value

    def __le__(self, other: int) -> bool:
        return self.value <= other.value

    def __gt__(self, other: int) -> bool:
        return self.value > other.value

    def __ge__(self, other: int) -> bool:
        return self.value >= other.value

    def __str__(self) -> str:
        return {
                self.MEMPLUS: "role_memberplus",
                self.MEMPRO: "role_memberpro",
                self.HELPER: "role_helper",
                self.MOD: "role_moderator",
                self.ADMIN: "role_administrator",
        }[self]

    def __eq__(self, other: Union[int, discord.Member, discord.interactions.Interaction]) -> bool:
        if isinstance(other, discord.interactions.Interaction):
            other = other.user

        if isinstance(other, discord.Member):
            if self == self.EVERYONE:
                return True
            if self == self.GUILD_OWNER:
                return other.guild.owner == other
            if self == self.OWNER:
                return other.id == cfg.owner_id

            return getattr(guild_service.get_guild(), str(self)) in list(map(lambda r: r.id, other.roles)) or self + 1 == other
        assert isinstance(other, self.__class__)
        return self.value == other.value

    def __add__(self, other) -> "PermissionLevel":
        return self.__class__(self.value + other)

    def __call__(self, command: discord.app_commands.Command) -> discord.app_commands.Command:
        if self == self.OWNER:
            command.checks.append(lambda ctx: True if self == ctx.user else MissingPermissionsError.throw(perms=[f"Bot Owner"]))
        elif self == self.GUILD_OWNER:
            command.checks.append(lambda ctx: True if self == ctx.user else MissingPermissionsError.throw(perms=[f"Guild Owner"]))
        else:
            command.checks.append(lambda ctx: True if self == ctx.user else MissingPermissionsError.throw(perms=[f"<@&{guild_service.get_guild()[self.__str__()]}>"]))
        return command

    def __hash__(self) -> int:
        return hash(self.value)


@unique
class RestrictionType(IntEnum):
    """Type of restriction enum"""

    CHANNEL = 0
    MEDIA = 1
    REACTION = 2
    CHATGPT = 3

    def __str__(self) -> str:
        return {
                self.CHANNEL: "role_channelrestriction",
                self.MEDIA: "role_mediarestriction",
                self.REACTION: "role_reactionrestriction",
                self.CHATGPT: "role_chatgptrestriction",
        }[self]

    def __hash__(self) -> int:
        return hash(self.value)
