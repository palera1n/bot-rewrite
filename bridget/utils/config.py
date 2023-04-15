from os import getenv


class Config:
    def __init__(self):
        self.guild_id = int(getenv("GUILD_ID"))
        self.owner_id = int(getenv("OWNER_ID"))


cfg = Config()