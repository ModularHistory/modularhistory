from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from apps.occurrences.models import Occurrence
from apps.quotes.models import Quote
from apps.sources.models import Source
from apps.entities.models import Entity

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
    context = fields.TextField(attr='context.text', analyzer=html_strip)
    date = fields.DateField(attr='date.string')
    attributees = fields.ObjectField(properties={
        'name': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.text')
    })
    citations = fields.TextField(attr='citations_text', analyzer=html_strip)
    topics = fields.ObjectField(attr='_related_topics', properties={
        'key': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.text', analyzer=html_strip)
    })

    class Django:
        model = Quote

        related_models = [Source, Entity]

    def get_queryset(self):
        return super(QuoteDocument, self).get_queryset().prefetch_related(
            'attributees', 'sources', 'topics'
        )