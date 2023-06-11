import discord

_NOPERMSERRORMSG = "You don't have permission to use this command."

class MissingPermissionsError(discord.app_commands.MissingPermissions):
    def __init__(self) -> None:
        super(_NOPERMSERRORMSG)
    
    def throw() -> None:
        raise discord.app_commands.MissingPermissionsError(_NOPERMSERRORMSG)
