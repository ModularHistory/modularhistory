from datetime import datetime
from itertools import chain

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.entities.models import Entity, entity
from apps.propositions.models import Occurrence, occurrence
from apps.quotes.models import Quote, quote


class TodayInHistoryViewSet(APIView):
    """API endpoint for today in history."""

    def get(self, request):
        today = datetime.now()

        todayinhistory_entity = Entity.objects.filter(
            Q(
                birth_date__year=today.year,
                birth_date__month=today.month,
                birth_date__day=today.day,
            )
            | Q(
                death_date__year=today.year,
                death_date__month=today.month,
                death_date__day=today.day,
            )
        )

        todayinhistory_occurrence = Occurrence.objects.filter(
            date__year=today.year, date__month=today.month, date__day=today.day
        )

        todayinhistory_quote = Quote.objects.filter(
            date__year=today.year, date__month=today.month, date__day=today.day
        )

        todayinhistory_result = list(
            chain(todayinhistory_entity, todayinhistory_occurrence, todayinhistory_quote)
        )
        return Response([model.serialize() for model in todayinhistory_result])
