from core.models.model import get_model_name

from .entity import (
    EntityCategoryInstantSearchDocument,
    EntityDocument,
    EntityInstantSearchDocument,
)
from .image import ImageDocument, ImageInstantSearchDocument
from .occurrence import OccurrenceDocument
from .place import PlaceInstantSearchDocument
from .proposition import PropositionDocument, PropositionInstantSearchDocument
from .quote import QuoteDocument, QuoteInstantSearchDocument
from .source import (
    SourceDocument,
    SourceDocumentCollectionInstantSearchDocument,
    SourceDocumentRepositoryInstantSearchDocument,
    SourceFileInstantSearchDocument,
    SourceInstantSearchDocument,
    SourcePublicationInstantSearchDocument,
    SourceWebsiteInstantSearchDocument,
)
from .topic import TopicInstantSearchDocument

instant_search_documents_map = {
    get_model_name(doc.Django.model): doc
    for doc in (
        TopicInstantSearchDocument,
        PlaceInstantSearchDocument,
        QuoteInstantSearchDocument,
        EntityInstantSearchDocument,
        EntityCategoryInstantSearchDocument,
        PropositionInstantSearchDocument,
        SourceInstantSearchDocument,
        SourcePublicationInstantSearchDocument,
        SourceDocumentCollectionInstantSearchDocument,
        SourceDocumentRepositoryInstantSearchDocument,
        SourceWebsiteInstantSearchDocument,
        SourceFileInstantSearchDocument,
        ImageInstantSearchDocument,
    )
}
