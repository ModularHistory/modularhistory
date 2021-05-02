from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.quotes.models import Quote
from apps.quotes.serializers import QuoteSerializer


class QuoteViewSet(ModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer


class QuoteListAPIView(ListAPIView):
    """API view for listing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer


class QuoteAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Quote.objects.all()
    lookup_field = 'slug'
    serializer_class = QuoteSerializer
