from django_elasticsearch_dsl import Document as ESDocument
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, instant_search_analyzer
from apps.topics.models.topic import Topic


@registry.register_document
class TopicInstantSearchDocument(ESDocument):
    """ElasticSearch document for topic used by search-as-you-type."""

    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'topics_instant_search'

    name = fields.TextField(analyzer=instant_search_analyzer)
    aliases = fields.TextField(analyzer=instant_search_analyzer)

    class Django:
        model = Topic
