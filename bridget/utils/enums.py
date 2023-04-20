import discord

from enum import IntEnum, unique
from discord.automod import AutoModRule
from typing import List, Optional, Union

from .services import guild_service
from .config import cfg


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

    def __eq__(self, other: Union[int, discord.Member]) -> bool:
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

    def check(self, ctx: discord.Interaction) -> bool:
        if not self == ctx.user:
            raise discord.app_commands.MissingPermissions(
                "You don't have permission to use this command.")
        return True

    def __call__(self, command: discord.app_commands.Command) -> discord.app_commands.Command:
        command.checks.append(self.check)
        return command

    def __hash__(self) -> int:
        return hash(self.value)


@unique
class FilterBypassLevel(IntEnum):
    """Filter bypass level enum"""

    HELPER = 0
    MOD = 1
    RAID = 2


    def __str__(self) -> str:
        return {
                self.HELPER: "Helper and up",
                self.MOD: "Moderator and up",
                self.RAID: "Raid phrases"
        }[self] 

    def find_rule_for_bypass(self, rules: List[AutoModRule]) -> Optional[AutoModRule]:
        if self == FilterBypassLevel.HELPER:
            # find the rule that has Helper exempt
            for rule in rules:
                if guild_service.get_guild().role_helper in rule.exempt_role_ids and not rule_has_timeout(rule):
                    return rule
            return None
        elif self == FilterBypassLevel.MOD:
            for rule in rules:
                # find the rule that doesnt have Helper exempt
                if guild_service.get_guild().role_helper not in rule.exempt_role_ids and not rule_has_timeout(rule):
                    return rule
            return None
        elif self == FilterBypassLevel.RAID:
            for rule in rules:
                # find the rule that times out the member
                if rule_has_timeout(rule):
                    return rule
            return None

        return None

