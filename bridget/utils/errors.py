import discord

#_NOPERMSERRORMSG = "You don't have permission to use this command."

class MissingPermissionsError(discord.app_commands.MissingPermissions):
    def __init__(self, perms) -> None:
        super().__init__(perms)

    @staticmethod
    def throw(perms: list = None) -> None:
        raise MissingPermissionsError(perms or [])
