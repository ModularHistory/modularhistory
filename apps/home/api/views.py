from datetime import datetime
from itertools import chain

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.entities.models import Entity
from apps.propositions.models import Occurrence
from apps.quotes.models import Quote


class TodayInHistoryViewSet(APIView):
    """API endpoint for today in history."""

    def get(self, request):
        today = datetime.now()

        print('before entitites')
        todayinhistory_entity = Entity.objects.filter(
            Q(
                birth_date__month=today.month,
                birth_date__day=today.day,
            )
            | Q(
                death_date__month=today.month,
                death_date__day=today.day,
            )
        )
        print('after entitites')
        todayinhistory_occurrence = Occurrence.objects.filter(
            date__month=today.month, date__day=today.day
        )
        print('after occurrences')

        todayinhistory_quote = Quote.objects.filter(
            date__month=today.month, date__day=today.day
        )
        print('after quotes')

        todayinhistory_result = chain(
            todayinhistory_entity, todayinhistory_occurrence, todayinhistory_quote
        )

        return Response([model.serialize() for model in todayinhistory_result])
