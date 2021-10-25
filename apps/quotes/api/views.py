from apps.quotes.api.serializers import QuoteDrfSerializer
from apps.quotes.models.quote import Quote
from core.api.views import ExtendedModelViewSet


class QuoteViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing quotes."""

    queryset = Quote.objects.all()
    serializer_class = QuoteDrfSerializer
    list_fields = ExtendedModelViewSet.list_fields | {
        'bite',
        'date_string',
        'primary_image',
    }
