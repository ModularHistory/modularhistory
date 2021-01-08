from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from modularhistory.views import AsyncAPIViewMixin
from apps.quotes.serializers import QuoteSerializer

from apps.quotes.models import Quote


class QuoteViewSet(ModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuoteListAPIView(AsyncAPIViewMixin, ListAPIView):
    """API view for listing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
