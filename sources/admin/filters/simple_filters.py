from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from modularhistory.constants import NO, YES, EMPTY_STRING
from sources.models import Source


class HasContainerFilter(SimpleListFilter):
    """Filter for whether the source has a container."""

    title = 'has container'
    parameter_name = 'has_container'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether containers exist."""
        if self.value() == YES:
            return queryset.exclude(containers=None)
        if self.value() == NO:
            return queryset.filter(containers=None)


class HasFileFilter(SimpleListFilter):
    """Filter for whether the source has a source file."""

    title = 'has file'
    parameter_name = 'has_file'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether source files exist."""
        if self.value() == YES:
            return queryset.filter(db_file__isnull=False).exclude(db_file__file=EMPTY_STRING)
        if self.value() == NO:
            return queryset.filter(Q(db_file__isnull=True) | Q(db_file__file=EMPTY_STRING))


class HasPageNumber(SimpleListFilter):
    """Filter for whether the source has a page number."""

    title = 'has page number'
    parameter_name = 'has_page_number'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether page numbers are specified."""
        queryset = queryset.filter(db_file__isnull=False).exclude(db_file__file=EMPTY_STRING)
        ids = []
        for source in queryset:
            source_object = getattr(source, 'obj', None) or source
            if hasattr(source_object, 'page_number'):
                has_page_number = bool(source_object.page_number)
                if self.value() == YES:
                    include_object = has_page_number
                elif self.value() == NO:
                    include_object = not has_page_number
                else:
                    include_object = True
                if include_object:
                    ids.append(source.id)
        return queryset.filter(id__in=ids)


class HasFilePageOffsetFilter(SimpleListFilter):
    """Filter for whether the source has a source file with a page offset."""

    title = 'has file page offset'
    parameter_name = 'has_file_page_offset'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether page offsets are specified."""
        sources = queryset.filter(db_file__isnull=False).exclude(db_file__file=EMPTY_STRING)
        ids = []
        if self.value() == YES:
            for source in sources:
                source_file = source.source_file
                if source_file.page_offset:
                    ids.append(source.id)
            return sources.filter(id__in=ids)
        elif self.value() == NO:
            for source in sources:
                source_file = source.source_file
                if not source_file.page_offset:
                    ids.append(source.id)
            return sources.filter(id__in=ids)


class ImpreciseDateFilter(SimpleListFilter):
    """TODO: add docstring."""
    title = 'date is imprecise'
    parameter_name = 'date_is_imprecise'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return (
            (YES, YES),
            # (NO, NO),
        )

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether dates are imprecise."""
        if self.value() == YES:
            return queryset.filter(date__second='01', date__minute='01', date__hour='01')
        return queryset


class TypeFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return Source._meta.get_field('type').choices

    def queryset(self, request, queryset):
        """Returns the queryset filtered by type."""
        type_value = self.value()
        if not type_value:
            return queryset
        return queryset.filter(type=type_value)
