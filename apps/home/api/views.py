from datetime import datetime
from itertools import chain

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.entities.models import Entity
from apps.propositions.models import Occurrence
from apps.quotes.models import Quote


class TodayInHistoryView(APIView):
    """API endpoint for today in history."""

    def get(self, request):
        today = datetime.now()
        today = datetime(2021, 7, 7)

        entities = Entity.objects.filter(
            Q(
                birth_date__month=today.month,
                birth_date__day=today.day,
            )
            | Q(
                death_date__month=today.month,
                death_date__day=today.day,
            )
        )

        occurrences = Occurrence.objects.filter(date__month=today.month, date__day=today.day)

        quotes = Quote.objects.filter(date__month=today.month, date__day=today.day)

        serialized_results = [
            instance.serialize() for instance in chain(entities, occurrences, quotes)
        ]
        from pprint import pprint

        pprint(serialized_results)

        return Response(serialized_results)
