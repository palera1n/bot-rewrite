import mongoengine


from _typeshed import Incomplete
class User(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    is_clem: Incomplete = mongoengine.BooleanField(default=False, required=True)
    is_xp_frozen: Incomplete = mongoengine.BooleanField(default=False, required=True)
    is_muted: Incomplete = mongoengine.BooleanField(default=False, required=True)
    is_music_banned: Incomplete = mongoengine.BooleanField(default=False, required=True)
    was_warn_kicked: Incomplete = mongoengine.BooleanField(default=False, required=True)
    birthday_excluded: Incomplete = mongoengine.BooleanField(default=False, required=True)
    raid_verified: Incomplete = mongoengine.BooleanField(default=False, required=True)

    xp: Incomplete = mongoengine.IntField(default=0, required=True)
    trivia_points: Incomplete = mongoengine.IntField(default=0, required=True)
    level: Incomplete = mongoengine.IntField(default=0, required=True)
    warn_points: Incomplete = mongoengine.IntField(default=0, required=True)

    offline_report_ping: Incomplete = mongoengine.BooleanField(
        default=False, required=True)

    timezone: Incomplete = mongoengine.StringField(default=None)
    birthday: Incomplete = mongoengine.ListField(default=[])
    sticky_roles: Incomplete = mongoengine.ListField(default=[])
    command_bans: Incomplete = mongoengine.DictField(default={})

    meta: Incomplete = {
        'db_alias': 'default',
        'collection': 'users'
    }
