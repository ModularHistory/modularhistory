from rest_framework.generics import RetrieveAPIView

from apps.flatpages.models import FlatPage
from apps.flatpages.serializers import FlatPageSerializer


class FlatPageAPIView(RetrieveAPIView):
    """API view for a single flat page."""

    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
    lookup_field = 'url'
