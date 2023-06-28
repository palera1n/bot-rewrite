import mongoengine
from .filterword import FilterWord
from .tag import Tag
from .issues import Issue


class Guild(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    infraction_id = mongoengine.IntField(min_value=1, required=True)
    reaction_role_mapping = mongoengine.DictField(default={})

    role_administrator = mongoengine.IntField()
    role_birthday = mongoengine.IntField()
    role_dev = mongoengine.IntField()
    role_helper = mongoengine.IntField()
    role_memberone = mongoengine.IntField()
    role_memberedition = mongoengine.IntField()
    role_memberplus = mongoengine.IntField()
    role_memberpro = mongoengine.IntField()
    role_memberultra = mongoengine.IntField()
    role_moderator = mongoengine.IntField()
    role_reportping = mongoengine.IntField()
    role_nicknamelock = mongoengine.IntField()
    role_mediarestriction = mongoengine.IntField()
    role_channelrestriction = mongoengine.IntField()
    role_reactionrestriction = mongoengine.IntField()
    role_chatgptrestriction = mongoengine.IntField()

    channel_botspam = mongoengine.IntField()
    channel_common_issues = mongoengine.IntField()
    channel_development = mongoengine.IntField()
    channel_emoji_log = mongoengine.IntField()
    channel_general = mongoengine.IntField()
    channel_support = mongoengine.IntField()
    channel_private = mongoengine.IntField()
    channel_msg_logs = mongoengine.IntField(default=0)
    channel_public = mongoengine.IntField()
    channel_rules = mongoengine.IntField()
    channel_reaction_roles = mongoengine.IntField()
    channel_reports = mongoengine.IntField()
    channel_chatgpt = mongoengine.IntField()
    channel_mempro_reports = mongoengine.IntField()

    emoji_logging_webhook = mongoengine.StringField()
    locked_channels = mongoengine.ListField(default=[])
    filter_excluded_channels = mongoengine.ListField(default=[])
    filter_excluded_guilds = mongoengine.ListField(default=[])
    filter_words = mongoengine.EmbeddedDocumentListField(
        FilterWord, default=[])
    raid_phrases = mongoengine.EmbeddedDocumentListField(
        FilterWord, default=[])
    logging_excluded_channels = mongoengine.ListField(default=[])
    tags = mongoengine.EmbeddedDocumentListField(Tag, default=[])
    memes = mongoengine.EmbeddedDocumentListField(Tag, default=[])
    ban_today_spam_accounts = mongoengine.BooleanField(default=False)
    issues = mongoengine.EmbeddedDocumentListField(Issue, default=[])
    issues_list_msg = mongoengine.ListField(default=[])

    meta = {
        'db_alias': 'default',
        'collection': 'guilds'
    }
