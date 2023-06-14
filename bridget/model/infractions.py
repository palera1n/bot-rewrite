import mongoengine
from .infraction import Infraction


class Infractions(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    infractions = mongoengine.EmbeddedDocumentListField(Infraction, default=[])

    meta = {
        'db_alias': 'default',
        'collection': 'infractions'
    }
