from apps.entities.api.serializers import (
    CategorizationSerializer,
    CategorySerializer,
    EntitySerializer,
)
from apps.images.api.serializers import ImageSerializer, VideoSerializer
from apps.moderation.serializers import ModeratedModelSerializer
from apps.places.api.serializers import PlaceSerializer
from apps.propositions.api.serializers import ArgumentSerializer
from apps.propositions.api.serializers import (
    CitationSerializer as PropositionCitationSerializer,
)
from apps.propositions.api.serializers import OccurrenceSerializer, PropositionSerializer
from apps.quotes.api.serializers import CitationSerializer, QuoteSerializer
from apps.sources.api.serializers import (
    SourceAttributionSerializer,
    SourceContainmentSerializer,
)
from apps.sources.api.sources.article.serializers import ArticleSerializer
from apps.sources.api.sources.book.serializers import BookSerializer, SectionSerializer
from apps.sources.api.sources.document.affidavit.serializers import AffidavitSerializer
from apps.sources.api.sources.document.collection.serializers import (
    CollectionSerializer,
    RepositorySerializer,
)
from apps.sources.api.sources.document.correspondence.serializers import (
    CorrespondenceSerializer,
)
from apps.sources.api.sources.document.serializers import DocumentSerializer
from apps.sources.api.sources.entry.serializers import EntrySerializer
from apps.sources.api.sources.file.serializers import SourceFileSerializer
from apps.sources.api.sources.film.serializers import FilmSerializer
from apps.sources.api.sources.interview.serializers import InterviewSerializer
from apps.sources.api.sources.piece.serializers import PieceSerializer
from apps.sources.api.sources.publication.serializers import (
    PublicationSerializer,
    WebpageSerializer,
    WebsiteSerializer,
)
from apps.sources.api.sources.report.serializers import ReportSerializer
from apps.sources.api.sources.speech.serializers import SpeechSerializer
from apps.topics.api.serializers import TopicSerializer

MODERATED_SERIALIZERS: list[ModeratedModelSerializer] = [
    EntitySerializer,
    CategorySerializer,
    CategorizationSerializer,
    QuoteSerializer,
    CitationSerializer,
    OccurrenceSerializer,
    PropositionSerializer,
    PropositionCitationSerializer,
    ArgumentSerializer,
    PlaceSerializer,
    TopicSerializer,
    ImageSerializer,
    VideoSerializer,
    SourceAttributionSerializer,
    SourceContainmentSerializer,
    ArticleSerializer,
    BookSerializer,
    SectionSerializer,
    DocumentSerializer,
    AffidavitSerializer,
    CorrespondenceSerializer,
    RepositorySerializer,
    CollectionSerializer,
    DocumentSerializer,
    EntrySerializer,
    FilmSerializer,
    InterviewSerializer,
    PieceSerializer,
    PublicationSerializer,
    WebpageSerializer,
    WebsiteSerializer,
    ReportSerializer,
    SpeechSerializer,
    SourceFileSerializer,
]
