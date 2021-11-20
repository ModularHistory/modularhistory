from rest_framework.response import Response
from rest_framework.views import APIView

from apps.moderation.models import ContentContribution


class ContentContributionAPIView(APIView):
    """API endpoint for content contribution."""

    def get(self, request):
        """Return the contents contributed"""
        results = ContentContribution.objects.filter(contributor=request.user)

        return Response([result.serialize() for result in results])
