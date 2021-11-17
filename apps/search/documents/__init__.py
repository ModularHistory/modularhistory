from core.models.model import get_model_name

from .entity import EntityDocument, EntityInstantSearchDocument
from .image import ImageDocument
from .occurrence import OccurrenceDocument
from .proposition import PropositionDocument, PropositionInstantSearchDocument
from .quote import QuoteDocument
from .source import SourceDocument
from .topic import TopicInstantSearchDocument

instant_search_documents_map = {
    get_model_name(doc.Django.model): doc
    for doc in (
        TopicInstantSearchDocument,
        EntityInstantSearchDocument,
        PropositionInstantSearchDocument,
    )
}
