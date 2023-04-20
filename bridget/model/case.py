import mongoengine
import datetime


from _typeshed import Incomplete
class Case(mongoengine.EmbeddedDocument):
    _id = mongoengine.IntField(required=True)
    _type = mongoengine.StringField(required=True)
    date: Incomplete = mongoengine.DateTimeField(
        default=datetime.datetime.now, required=True)
    until: Incomplete = mongoengine.DateTimeField(default=None)
    mod_id: Incomplete = mongoengine.IntField(required=True)
    mod_tag: Incomplete = mongoengine.StringField(required=True)
    reason: Incomplete = mongoengine.StringField(required=True)
    punishment: Incomplete = mongoengine.StringField()
    lifted: Incomplete = mongoengine.BooleanField(default=False)
    lifted_by_tag: Incomplete = mongoengine.StringField()
    lifted_by_id: Incomplete = mongoengine.IntField()
    lifted_reason: Incomplete = mongoengine.StringField()
    lifted_date: Incomplete = mongoengine.DateField()
