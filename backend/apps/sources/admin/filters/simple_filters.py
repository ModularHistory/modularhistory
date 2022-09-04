"""Simple list filters for the source admin."""

from django.db.models import Count, Q

from apps.admin.list_filters import BooleanListFilter, PolymorphicContentTypeFilter
from apps.sources.models.source import Source
from core.constants.strings import EMPTY_STRING, NO, YES


class HasContainerFilter(BooleanListFilter):
    """Filters sources by whether they have a container."""

    title = 'has container'
    parameter_name = 'has_container'

    def queryset(self, request, queryset):
        """Return the queryset filtered by whether containers exist."""
        if self.value() == YES:
            return queryset.exclude(containers=None)
        if self.value() == NO:
            return queryset.filter(containers=None)


class HasFileFilter(BooleanListFilter):
    """Filters sources by whether they have a source file."""

    title = 'has file'
    parameter_name = 'has_file'

    def queryset(self, request, queryset):
        """Return the queryset filtered by whether source files exist."""
        if self.value() == YES:
            filters = {'file__isnull': False}
            exclusions = {'file__file': EMPTY_STRING}
            return queryset.filter(**filters).exclude(**exclusions)
        if self.value() == NO:
            file_is_null = {'file__isnull': True}
            file_is_empty = {'file__file': EMPTY_STRING}
            return queryset.filter(Q(**file_is_null) | Q(**file_is_empty))


class HasFilePageOffsetFilter(BooleanListFilter):
    """Filters sources by whether they have a source file with a page offset."""

    title = 'has file page offset'
    parameter_name = 'has_file_page_offset'

    def queryset(self, request, queryset):
        """Return the queryset filtered by whether page offsets are specified."""
        sources = queryset.filter(db_file__isnull=False).exclude(db_file__file=EMPTY_STRING)
        ids = []
        include_if_has_page_offset = self.value() == YES
        for source in sources:
            source_file = source.file
            if bool(source_file.page_offset) == include_if_has_page_offset:
                ids.append(source.pk)
        return sources.filter(id__in=ids)


class HasMultipleSourcesFilter(BooleanListFilter):
    """Filter for whether model instances have multiple sources."""

    title = 'has multiple sources'
    parameter_name = 'has_multiple_sources'

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        queryset = queryset.annotate(citation_count=Count('sources'))
        if self.value() == YES:
            return queryset.exclude(citation_count__lt=2)
        if self.value() == NO:
            return queryset.filter(citation_count__gte=2)


class HasSourceFilter(BooleanListFilter):
    """Filter for whether model instances have a source."""

    title = 'has source'
    parameter_name = 'has_source'

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        if self.value() == YES:
            return queryset.exclude(sources=None)
        if self.value() == NO:
            return queryset.filter(sources=None)


class ImpreciseDateFilter(BooleanListFilter):
    """Filters sources by whether their dates are imprecise."""

    title = 'date is imprecise'
    parameter_name = 'date_is_imprecise'

    def queryset(self, request, queryset):
        """Return the queryset filtered by whether dates are imprecise."""
        if self.value() == YES:
            return queryset.filter(date__second='01', date__minute='01', date__hour='01')
        return queryset


class SourceTypeFilter(PolymorphicContentTypeFilter):
    """Filters sources by type."""

    base_model = Source
