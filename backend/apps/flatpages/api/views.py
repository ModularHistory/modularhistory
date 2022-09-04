from rest_framework.generics import RetrieveAPIView

from apps.flatpages.api.serializers import FlatPageSerializer
from apps.flatpages.models import FlatPage


class FlatPageAPIView(RetrieveAPIView):
    """API view for a single flat page."""

    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
    lookup_field = 'path'
