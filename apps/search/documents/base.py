from django_elasticsearch_dsl import Document as ESDocument
from django_elasticsearch_dsl import fields


class Document(ESDocument):

    verified = fields.BooleanField()
    date = fields.DateField()

    @staticmethod
    def prepare_date(instance):
        return instance.get_date()

    @classmethod
    def get_index_name(cls, index=None):
        return cls._default_index(index)
