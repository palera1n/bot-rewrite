import mongoengine

from . import User

class PGPKey(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    key = mongoengine.BinaryField(default=None, required=True)
    key_signature = mongoengine.StringField(default=None)
    full_name = mongoengine.StringField(default=None)
    email = mongoengine.StringField(default=None)
    user = mongoengine.ReferenceField(User, required=True)

    meta = {
        'db_alias': 'default',
        'collection': 'pgpkeys'
    }