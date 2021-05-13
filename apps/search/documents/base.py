from django_elasticsearch_dsl import Document as ESDocument
from django_elasticsearch_dsl import fields


class Document(ESDocument):

    hidden = fields.BooleanField()
    verified = fields.BooleanField()
    date = fields.DateField()
    date_year = fields.IntegerField()

    @staticmethod
    def prepare_date(instance):
        return instance.get_date()

    @staticmethod
    def prepare_date_year(instance):
        date = instance.get_date()
        return date.year if date else None

    @classmethod
    def get_index_name(cls, index=None):
        return cls._default_index(index)
