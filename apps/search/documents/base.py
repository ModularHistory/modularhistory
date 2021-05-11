from django_elasticsearch_dsl import Document as ESDocument
from django_elasticsearch_dsl import fields


class Document(ESDocument):

    hidden = fields.BooleanField()
    verified = fields.BooleanField()

    @classmethod
    def index_name(cls, index=None):
        return cls._default_index(index)
