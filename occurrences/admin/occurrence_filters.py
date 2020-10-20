from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q

from modularhistory.constants import NO, YES


class EntityFilter(AutocompleteFilter):
    """Filters occurrences by involved entities."""

    title = 'entity'
    field_name = 'involved_entities'


class LocationFilter(AutocompleteFilter):
    """Filters occurrences by location."""

    title = 'location'
    field_name = 'locations'


class HasQuotesFilter(SimpleListFilter):
    """Filters occurrences by whether they have associated quotes."""

    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Returns the filtered queryset."""
        queryset = queryset.annotate(quote_count=Count('quote_relations'))
        if self.value() == YES:
            return queryset.exclude(quote_count__lt=1)
        if self.value() == NO:
            return queryset.filter(quote_count__gt=1)
        return queryset


class HasDateFilter(SimpleListFilter):
    """Filters occurrences by whether they have dates."""

    title = 'has date'
    parameter_name = 'has_date'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Returns the filtered queryset."""
        if self.value() == YES:
            return queryset.filter(date__isnull=False).exclude(date='')
        if self.value() == NO:
            return queryset.filter(Q(date__isnull=True) | Q(date=''))
