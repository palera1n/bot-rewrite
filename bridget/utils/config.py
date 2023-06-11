from os import getenv


class Config:
    def __init__(self) -> None:
        self.guild_id = int(getenv("GUILD_ID"))
        self.ban_appeal_guild_id = int(getenv("APPEAL_GUILD_ID"))
        self.ban_appeal_mod_role = int(getenv("APPEAL_MOD_ROLE"))
        self.owner_id = int(getenv("OWNER_ID"))
        self.prefix = str(getenv("PREFIX"))


cfg = Config()
