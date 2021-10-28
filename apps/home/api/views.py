
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.home.models import Feature


class FeatureAPIView(APIView):
    """API endpoint for featured contents."""

    def get(self, request):
        """Return the featured query"""
        now = timezone.now()

        results = Feature.objects.filter(
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        )
        # results = Feature.objects.all()
        return Response([result.content_object.serialize() for result in results])
        # return Response([Feature.objects.count()])
