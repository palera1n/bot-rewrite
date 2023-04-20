from os import getenv


from _typeshed import Incomplete
class Config:
    guild_id: Incomplete
    owner_id: Incomplete
    prefix: Incomplete
    def __init__(self) -> None:
        self.guild_id = int(getenv("GUILD_ID"))
        self.owner_id = int(getenv("OWNER_ID"))
        self.prefix = str(getenv("PREFIX"))


cfg: Incomplete = Config()
