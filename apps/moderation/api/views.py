from typing import TYPE_CHECKING

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.moderation.api.serializers import ContentContributionSerializer
from apps.moderation.models.contribution import ContentContribution

if TYPE_CHECKING:
    from rest_framework.request import Request


class ContentContributionAPIView(APIView):
    """API endpoint for content contribution."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: 'Request'):
        """Return the contents contributed"""
        contributions = ContentContribution.objects.filter(contributor=request.user)
        return (
            Response([ContentContributionSerializer(result).data for result in contributions])
            if contributions
            else Response([])
        )
