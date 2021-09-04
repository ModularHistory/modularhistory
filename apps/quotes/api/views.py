from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView

from apps.quotes.models.quote import Quote
from apps.quotes.api.serializers import QuoteModelSerializer


class QuoteViewSet(ModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QuoteAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Quote.objects.all()
    lookup_field = 'slug'
    serializer_class = QuoteModelSerializer
