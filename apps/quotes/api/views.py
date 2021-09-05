from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.quotes.api.serializers import QuoteModelSerializer
from apps.quotes.models.quote import Quote


class QuoteViewSet(ModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    lookup_field = 'slug'
    serializer_class = QuoteModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
