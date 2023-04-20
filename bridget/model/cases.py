import mongoengine
from .case import Case


from .case import Case as Case
from _typeshed import Incomplete
from .case import Case as Case
class Cases(mongoengine.Document):
    _id = mongoengine.IntField(required=True)
    cases: Incomplete = mongoengine.EmbeddedDocumentListField(Case, default=[])

    meta: Incomplete = {
        'db_alias': 'default',
        'collection': 'cases'
    }
