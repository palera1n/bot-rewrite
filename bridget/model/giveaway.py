import mongoengine


from _typeshed import Incomplete
class Giveaway(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    is_ended: Incomplete = mongoengine.BooleanField(default=False)
    end_time: Incomplete = mongoengine.DateTimeField()
    channel: Incomplete = mongoengine.IntField()
    name: Incomplete = mongoengine.StringField()
    entries: Incomplete = mongoengine.ListField(mongoengine.IntField(), default=[])
    previous_winners: Incomplete = mongoengine.ListField(
        mongoengine.IntField(), default=[])
    sponsor: Incomplete = mongoengine.IntField()
    winners: Incomplete = mongoengine.IntField()

    meta: Incomplete = {
        'db_alias': 'default',
        'collection': 'giveaways'
    }
