from apps.quotes.api.serializers import QuoteSerializer
from apps.quotes.models.quote import Quote
from core.api.views import ExtendedModelViewSet


class QuoteViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    list_fields = ExtendedModelViewSet.list_fields | {
        'bite',
        'date_string',
        'primary_image',
    }
