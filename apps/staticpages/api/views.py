from rest_framework.generics import RetrieveAPIView

from apps.staticpages.models import StaticPage
from apps.staticpages.serializers import StaticPageSerializer


class StaticPageAPIView(RetrieveAPIView):
    """API view for a single static page."""

    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = "url"
