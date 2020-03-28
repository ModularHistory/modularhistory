from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Count


class TopicFilter(AutocompleteFilter):
    title = 'topic'
    field_name = 'related_topics'


class AttributeeFilter(AutocompleteFilter):
    title = 'attributee'
    field_name = '_attributee'


class AttributeeClassificationFilter(AutocompleteFilter):
    title = 'attributee classification'
    field_name = 'attributee__classifications'


class HasSourceFilter(SimpleListFilter):
    title = 'has source'
    parameter_name = 'has_source'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.exclude(sources=None)
        if self.value() == 'No':
            return queryset.filter(sources=None)


class AttributeeCountFilter(SimpleListFilter):
    title = 'attributee count'
    parameter_name = 'attributee_count'

    def lookups(self, request, model_admin):
        return (
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4+'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(attributee_count=Count('attributees'))
        try:
            n = int(self.value())
        except TypeError:  # `All`
            return queryset
        if n == 4:
            return queryset.exclude(attributee_count__lt=n)
        return queryset.filter(attributee_count=n)


class HasMultipleCitationsFilter(SimpleListFilter):
    title = 'has multiple citations'
    parameter_name = 'has_multiple_citations'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(citation_count=Count('citations'))
        if self.value() == 'Yes':
            return queryset.exclude(citation_count__lt=2)
        if self.value() == 'No':
            return queryset.filter(citation_count__gte=2)
