import mongoengine

class PGPKey(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    key = mongoengine.BinaryField(default=None, required=True)
    key_signature = mongoengine.StringField(default=None)
    full_name = mongoengine.StringField(default=None)
    email = mongoengine.StringField(default=None)
    user = mongoengine.IntField(default=None)

    meta = {
        'db_alias': 'default',
        'collection': 'pgpkeys'
    }