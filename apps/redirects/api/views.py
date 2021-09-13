from rest_framework.generics import ListAPIView
from rest_framework.serializers import ModelSerializer

from apps.redirects.models import Redirect


class RedirectSerializer(ModelSerializer):
    class Meta:
        model = Redirect
        fields = '__all__'


class RedirectListAPIView(ListAPIView):
    """API view for listing all redirects."""

    queryset = Redirect.objects.all()
    serializer_class = RedirectSerializer
