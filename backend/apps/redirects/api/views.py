from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.serializers import ModelSerializer

from apps.redirects.models import Redirect


class RedirectSerializer(ModelSerializer):
    class Meta:
        model = Redirect
        fields = '__all__'


class RedirectListAPIView(ListAPIView):
    """API view for listing all redirects."""

    queryset = Redirect.objects.filter(site_id=settings.SITE_ID)
    serializer_class = RedirectSerializer


class RedirectAPIView(RetrieveAPIView):
    """API view for retrieving a redirect for a given path."""

    queryset = Redirect.objects.filter(site_id=settings.SITE_ID)
    serializer_class = RedirectSerializer
    lookup_field = 'old_path'
