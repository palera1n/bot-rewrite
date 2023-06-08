import mongoengine
from datetime import datetime


class Issue(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    content = mongoengine.StringField(required=True)
    added_by_tag = mongoengine.StringField()
    added_by_id = mongoengine.IntField()
    added_date = mongoengine.DateTimeField(default=datetime.now)
    image = mongoengine.FileField(default=None)
    button_links = mongoengine.ListField(default=[], required=False)
    message_id = mongoengine.IntField()
    panic_string = mongoengine.StringField()
