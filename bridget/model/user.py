import mongoengine

class PGPKey(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    key = mongoengine.BinaryField(default=None, required=True)
    key_signature = mongoengine.StringField(default=None)
    full_name = mongoengine.StringField(default=None)
    email = mongoengine.StringField(default=None)
    user = mongoengine.IntField(default=None)

    meta = {
        'db_alias': 'default',
        'collection': 'pgpkeys'
    }

class User(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    is_clem = mongoengine.BooleanField(default=False, required=True)
    is_xp_frozen = mongoengine.BooleanField(default=False, required=True)
    is_muted = mongoengine.BooleanField(default=False, required=True)
    is_music_banned = mongoengine.BooleanField(default=False, required=True)
    was_warn_kicked = mongoengine.BooleanField(default=False, required=True)
    birthday_excluded = mongoengine.BooleanField(default=False, required=True)
    raid_verified = mongoengine.BooleanField(default=False, required=True)

    xp = mongoengine.IntField(default=0, required=True)
    trivia_points = mongoengine.IntField(default=0, required=True)
    level = mongoengine.IntField(default=0, required=True)
    warn_points = mongoengine.IntField(default=0, required=True)

    offline_report_ping = mongoengine.BooleanField(
        default=False, required=True)

    timezone = mongoengine.StringField(default=None)
    birthday = mongoengine.ListField(default=[])
    sticky_roles = mongoengine.ListField(default=[])
    command_bans = mongoengine.DictField(default={})

    meta = {
        'db_alias': 'default',
        'collection': 'users'
    }
