from rest_framework import permissions

from apps.quotes.api.serializers import QuoteDrfSerializer
from apps.quotes.models.quote import Quote
from core.api.views import ExtendedModelViewSet


class QuoteViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    lookup_field = 'slug'
    serializer_class = QuoteDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
