from rest_framework import permissions
from rest_framework.generics import ListAPIView
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
