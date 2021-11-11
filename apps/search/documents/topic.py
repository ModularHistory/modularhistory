from apps.search.documents.base import InstantSearchDocumentFactory
from apps.topics.models.topic import Topic

TopicInstantSearchDocument = InstantSearchDocumentFactory(Topic, ['name', 'aliases'])
