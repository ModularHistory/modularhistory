from typing import Type

from django_elasticsearch_dsl import Document as ESDocument
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, instant_search_analyzer
from core.models.module import Module


class Document(ESDocument):

    verified = fields.BooleanField()
    date = fields.DateField()

    @staticmethod
    def prepare_date(instance):
        return instance.get_date()

    @classmethod
    def get_index_name(cls, index=None):
        return cls._default_index(index)


def InstantSearchDocumentFactory(model: Type[Module], field_names: list[str], register=True):
    """Returns an ElasticSearch Document class for the given module class.

    All fields are analyzed as instant-search text fields.
    The generated document is automatically registered by default.
    """
    instant_search_fields = {}
    for field in field_names:
        if not hasattr(model, field):
            raise AttributeError(f'model {model} does not have attribute "{field}"')
        instant_search_fields[field] = fields.TextField(analyzer=instant_search_analyzer)

    document_class = type(
        f'{model.__name__}InstantSearchDocument',
        (ESDocument,),
        {
            'Index': type(
                'Index',
                (),
                {
                    'name': f'{model.__name__.lower()}_instant_search',
                    'settings': DEFAULT_INDEX_SETTINGS,
                },
            ),
            'Django': type('Django', (), {'model': model}),
            **instant_search_fields,
        },
    )

    if register:
        registry.register_document(document_class)
    return document_class
