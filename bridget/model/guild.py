import mongoengine
from .filterword import FilterWord
from .tag import Tag


from .filterword import FilterWord as FilterWord
from .tag import Tag as Tag
from _typeshed import Incomplete
from .filterword import FilterWord as FilterWord
from .tag import Tag as Tag
class Guild(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    case_id: Incomplete = mongoengine.IntField(min_value=1, required=True)
    reaction_role_mapping: Incomplete = mongoengine.DictField(default={})

    role_administrator: Incomplete = mongoengine.IntField()
    role_birthday: Incomplete = mongoengine.IntField()
    role_dev: Incomplete = mongoengine.IntField()
    role_helper: Incomplete = mongoengine.IntField()
    role_memberone: Incomplete = mongoengine.IntField()
    role_memberedition: Incomplete = mongoengine.IntField()
    role_memberplus: Incomplete = mongoengine.IntField()
    role_memberpro: Incomplete = mongoengine.IntField()
    role_memberultra: Incomplete = mongoengine.IntField()
    role_moderator: Incomplete = mongoengine.IntField()

    channel_botspam: Incomplete = mongoengine.IntField()
    channel_common_issues: Incomplete = mongoengine.IntField()
    channel_development: Incomplete = mongoengine.IntField()
    channel_emoji_log: Incomplete = mongoengine.IntField()
    channel_general: Incomplete = mongoengine.IntField()
    channel_support: Incomplete = mongoengine.IntField()
    channel_private: Incomplete = mongoengine.IntField()
    channel_msg_logs: Incomplete = mongoengine.IntField(default=0)
    channel_public: Incomplete = mongoengine.IntField()
    channel_rules: Incomplete = mongoengine.IntField()
    channel_reaction_roles: Incomplete = mongoengine.IntField()
    channel_reports: Incomplete = mongoengine.IntField()
    channel_chatgpt: Incomplete = mongoengine.IntField()
    channel_mempro_reports: Incomplete = mongoengine.IntField()

    emoji_logging_webhook: Incomplete = mongoengine.StringField()
    locked_channels: Incomplete = mongoengine.ListField(default=[])
    filter_excluded_channels: Incomplete = mongoengine.ListField(default=[])
    filter_excluded_guilds: Incomplete = mongoengine.ListField(default=[])
    filter_words: Incomplete = mongoengine.EmbeddedDocumentListField(
        FilterWord, default=[])
    raid_phrases: Incomplete = mongoengine.EmbeddedDocumentListField(
        FilterWord, default=[])
    logging_excluded_channels: Incomplete = mongoengine.ListField(default=[])
    tags: Incomplete = mongoengine.EmbeddedDocumentListField(Tag, default=[])
    memes: Incomplete = mongoengine.EmbeddedDocumentListField(Tag, default=[])
    ban_today_spam_accounts: Incomplete = mongoengine.BooleanField(default=False)

    meta: Incomplete = {
        'db_alias': 'default',
        'collection': 'guilds'
    }
