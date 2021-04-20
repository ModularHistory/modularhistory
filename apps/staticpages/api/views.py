from rest_framework.generics import RetrieveAPIView
from apps.staticpages.serializers import StaticPageSerializer
from apps.staticpages.models import StaticPage


class StaticPageAPIView(RetrieveAPIView):
    """API view for a single static page."""

    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = "url"
