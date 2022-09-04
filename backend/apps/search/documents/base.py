from typing import Type

from django_elasticsearch_dsl import Document as ESDocument
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, instant_search_analyzer
from core.models import ExtendedModel
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


class InstantSearchDocument(ESDocument):
    search_fields: list[str]
    filter_fields: list[str]


def InstantSearchDocumentFactory(
    model: Type[ExtendedModel],
    search_fields: list[str],
    filter_fields: list[str] = None,
    field_kwargs: dict = None,
    register=True,
):
    """Returns an ElasticSearch Document class for the given module class.

    All fields are analyzed as instant-search text fields.
    The generated document is automatically registered by default.
    """
    filter_fields = filter_fields or []
    field_kwargs = field_kwargs or {}

    # verify that all fields are valid via field name or attr provided by field_kwargs
    for field in search_fields + filter_fields:
        if not hasattr(model, field):
            if field in field_kwargs and not hasattr(
                model, field_kwargs.get(field).get('attr', None)
            ):
                field = field_kwargs.get(field).get('attr', None)
            else:
                continue
            raise AttributeError(f'Model {model} does not have attribute "{field}"')

    instant_search_fields = {
        field: fields.TextField(
            analyzer=instant_search_analyzer, **(field_kwargs.get(field) or {})
        )
        for field in search_fields
    }
    keyword_fields = {field: fields.KeywordField() for field in filter_fields}

    document_class = type(
        f'{model.__name__}InstantSearchDocument',
        (InstantSearchDocument,),
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
            'search_fields': search_fields,
            'filter_fields': filter_fields,
            **instant_search_fields,
            **keyword_fields,
        },
    )

    if register:
        registry.register_document(document_class)
    return document_class
