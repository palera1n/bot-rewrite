from os import getenv
from logging import warn

class Config:
    def __init__(self) -> None:
        self.guild_id = int(getenv("GUILD_ID"))
        try:
            self.ban_appeal_guild_id = int(getenv("APPEAL_GUILD_ID"))
            self.ban_appeal_mod_role = int(getenv("APPEAL_MOD_ROLE"))
        except TypeError:
            warn("APPEAL_* was not defined, diabling appeals")
            self.ban_appeal_guild_id = -1
            self.ban_appeal_mod_role = -1
        self.owner_id = int(getenv("OWNER_ID"))
        self.prefix = str(getenv("PREFIX"))


cfg = Config()
