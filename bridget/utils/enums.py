import discord
from .services import guild_service
from .config import cfg


from enum import IntEnum, unique, auto

@unique
class PermissionLevel(IntEnum):
    """Permission level enum"""
    
    
    EVERYONE = 0
    MEMPLUS = 1
    MEMPRO = 2
    HELPER = 3
    MOD = 4
    ADMIN = 5
    OWNER = 6


    # Checks
    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __eq__(self, other):

        if isinstance(other, discord.Member):
            if self == self.__class__.EVERYONE:
                return True
            if self == self.__class__.OWNER:
                return other.id == cfg.owner_id
            
            return getattr(guild_service.get_guild(), {
                self.__class__.MEMPLUS: "role_memberplus",
                self.__class__.MEMPRO: "role_memberpro",
                self.__class__.HELPER: "role_helper",
                self.__class__.MOD: "role_moderator",
                self.__class__.ADMIN: "role_administrator",
            }[self]) in list(map(lambda r: r.id, other.roles)) or self + 1 == other
            
        return self.value == other.value
    
    def __add__(self, other):
        return self.__class__(self.value + other)
    
    def check(self, ctx: discord.Interaction):
        if not self == ctx.user:
            raise discord.app_commands.MissingPermissions("You don't have permission to use this command.")
        return True
    
    def __call__(self, command: discord.app_commands.Command):
        command.checks.append(self.check)
        return command

    def __hash__(self):
        return hash(self.value)
