from itertools import chain

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.entities.models import Entity
from apps.propositions.models import Occurrence
from apps.quotes.models import Quote


class FeaturedContentViewSet(APIView):
    """API endpoint for featured contents."""

    def get(self, request):
        """Return the featured query"""

        featured_entity = Entity.objects.all()
        featured_occurence = Occurrence.objects.all()
        featured_quote = Quote.objects.all()

        featured_contents = chain(featured_entity, featured_occurence, featured_quote)

        return Response([instance.serialize() for instance in featured_contents])
