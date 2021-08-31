from django.contrib.flatpages.models import FlatPage
from rest_framework.generics import RetrieveAPIView

from apps.staticpages.serializers import FlatPageSerializer


class FlatPageAPIView(RetrieveAPIView):
    """API view for retrieving the content of a single flatpage."""

    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
    lookup_field = 'url'
