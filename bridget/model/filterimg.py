import mongoengine


class FilterWord(mongoengine.EmbeddedDocument):
    hash = mongoengine.StringField()
    
