from apps.entities.map import EntitiesMap
from apps.flatpages.map import FlatPagesMap
from apps.images.map import ImagesMap
from apps.propositions.map import PropositionsMap
from apps.quotes.map import QuotesMap
from apps.sources.map import SourcesMap
from apps.topics.map import TopicsMap

sitemaps = {
    'entities': EntitiesMap,
    'flatpages': FlatPagesMap,
    'images': ImagesMap,
    'propositions': PropositionsMap,
    'quotes': QuotesMap,
    'sources': SourcesMap,
    'topics': TopicsMap,
}
