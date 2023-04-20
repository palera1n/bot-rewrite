import mongoengine


from _typeshed import Incomplete
class FilterWord(mongoengine.EmbeddedDocument):
    notify: Incomplete = mongoengine.BooleanField(required=True)
    bypass: Incomplete = mongoengine.IntField(required=True)
    word: Incomplete = mongoengine.StringField(required=True)
    false_positive: Incomplete = mongoengine.BooleanField(default=False)
    piracy: Incomplete = mongoengine.BooleanField(default=False)
