import mongoengine
from datetime import datetime


from _typeshed import Incomplete
class Tag(mongoengine.EmbeddedDocument):
    name: Incomplete = mongoengine.StringField(required=True)
    content: Incomplete = mongoengine.StringField(required=True)
    added_by_tag: Incomplete = mongoengine.StringField()
    added_by_id: Incomplete = mongoengine.IntField()
    added_date: Incomplete = mongoengine.DateTimeField(default=datetime.now)
    use_count: Incomplete = mongoengine.IntField(default=0)
    image: Incomplete = mongoengine.FileField(default=None)
    button_links: Incomplete = mongoengine.ListField(default=[], required=False)
