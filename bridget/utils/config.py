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
        try:
            self.backend_client_id = getenv("CLIENT_ID")
            self.backend_client_secret = getenv("CLIENT_SECRET")
            self.backend_port = int(getenv("BACKEND_PORT"))
            self.backend_appeals_channel = int(getenv("BACKEND_APPEALS_CHANNEL"))
        except TypeError:
            warn("backend env vars were not defined, diabling backend")
            self.backend_client_id = ""
            self.backend_client_secret = ""
            self.backend_port = -1
            self.backend_appeals_channel = -1
        self.owner_id = int(getenv("OWNER_ID"))
        self.prefix = str(getenv("PREFIX"))


cfg = Config()
