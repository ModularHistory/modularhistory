from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from apps.occurrences.models import Occurrence
from apps.quotes.models import Quote
from apps.sources.models import Source

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

@registry.register_document
class QuoteDocument(Document):
    class Index:
        name = 'quotes'

        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    text = fields.TextField(attr='text.text', analyzer=html_strip)
    date = fields.DateField(attr='date.string')
    attributees = fields.ObjectField(properties={
        'name': fields.TextField()
    })
    # citations = fields.ObjectField(properties={
    #     'string': fields.TextField()
    # })

    class Django:
        model = Quote

        related_models = [Source]

    def get_queryset(self):
        return super(QuoteDocument, self).get_queryset().prefetch_related(
            'attributees', 'sources'
        )