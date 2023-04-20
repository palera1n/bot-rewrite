import mongoengine


from _typeshed import Incomplete
class Giveaway(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    is_ended: mongoengine.BooleanField = mongoengine.BooleanField(default=False)
    end_time: mongoengine.DateTimeField = mongoengine.DateTimeField()
    channel: mongoengine.IntField = mongoengine.IntField()
    name: mongoengine.StringField = mongoengine.StringField()
    entries: mongoengine.ListField = mongoengine.ListField(mongoengine.IntField(), default=[])
    previous_winners: mongoengine.ListField = mongoengine.ListField(
        mongoengine.IntField(), default=[])
    sponsor: mongoengine.IntField = mongoengine.IntField()
    winners: mongoengine.IntField = mongoengine.IntField()

    meta: Incomplete = {
        'db_alias': 'default',
        'collection': 'giveaways'
    }
