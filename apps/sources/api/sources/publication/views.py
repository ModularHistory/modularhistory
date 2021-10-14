from apps.sources.api.sources.publication.serializers import (
    PublicationDrfSerializer,
    WebpageDrfSerializer,
    WebsiteDrfSerializer,
)
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Publication, Webpage, Website
from core.api.views import ExtendedModelViewSet


class WebpageViewSet(SourceViewSet):
    """API endpoint for viewing and editing webpage sources."""

    queryset = Webpage.objects.all()
    serializer_class = WebpageDrfSerializer


class PublicationViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing publication sources."""

    queryset = Publication.objects.all()
    serializer_class = PublicationDrfSerializer
    list_fields = None


class WebsiteViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing website sources."""

    queryset = Website.objects.all()
    serializer_class = WebsiteDrfSerializer
    list_fields = None
