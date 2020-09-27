from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q


class EntityFilter(AutocompleteFilter):
    """TODO: add docstring."""

    title = 'entity'
    field_name = 'involved_entities'


# class TopicFilter(AutocompleteFilter):
#     title = 'topic'
#     field_name = 'related_topics'


class LocationFilter(AutocompleteFilter):
    """TODO: add docstring."""

    title = 'location'
    field_name = 'locations'


class HasQuotesFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        queryset = queryset.annotate(quote_count=Count('quote_relations'))
        if self.value() == 'Yes':
            return queryset.exclude(quote_count__lt=1)
        if self.value() == 'No':
            return queryset.filter(quote_count__gt=1)
        return queryset


class HasDateFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has date'
    parameter_name = 'has_date'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.filter(date__isnull=False).exclude(date='')
        if self.value() == 'No':
            return queryset.filter(Q(date__isnull=True) | Q(date=''))
