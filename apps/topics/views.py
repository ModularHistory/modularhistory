from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.db.models.query import QuerySet

from apps.topics.models.topic import Topic


class TagSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self) -> 'QuerySet[Topic]':
        """Return the filtered queryset."""
        queryset = Topic.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(key__icontains=term) | Q(aliases__icontains=term)
            )
        return queryset
