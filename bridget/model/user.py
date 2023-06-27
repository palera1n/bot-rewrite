import mongoengine

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

    is_appealing = mongoengine.BooleanField(default=False)
    is_banned = mongoengine.BooleanField(default=False)
    last_appeal_date = mongoengine.DateField()
    last_ban_date = mongoengine.DateField()
    ban_count = mongoengine.IntField(default=0)
    appeal_btn_msg_id = mongoengine.IntField()

    meta = {
        'db_alias': 'default',
        'collection': 'users'
    }
