from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from admin.list_filters import BooleanListFilter
from modularhistory.constants import EMPTY_STRING, NO, YES
from sources.models import Source


class HasContainerFilter(BooleanListFilter):
    """Filters sources by whether they have a container."""

    title = 'has container'
    parameter_name = 'has_container'

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether containers exist."""
        if self.value() == YES:
            return queryset.exclude(containers=None)
        if self.value() == NO:
            return queryset.filter(containers=None)


class HasFileFilter(BooleanListFilter):
    """Filters sources by whether they have a source file."""

    title = 'has file'
    parameter_name = 'has_file'

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether source files exist."""
        if self.value() == YES:
            return queryset.filter(db_file__isnull=False).exclude(db_file__file=EMPTY_STRING)
        if self.value() == NO:
            return queryset.filter(Q(db_file__isnull=True) | Q(db_file__file=EMPTY_STRING))


class HasPageNumber(BooleanListFilter):
    """Filters sources by whether they have a page number."""

    title = 'has page number'
    parameter_name = 'has_page_number'

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


class HasFilePageOffsetFilter(BooleanListFilter):
    """Filters sources by whether they have a source file with a page offset."""

    title = 'has file page offset'
    parameter_name = 'has_file_page_offset'

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


class ImpreciseDateFilter(BooleanListFilter):
    """Filters sources by whether their dates are imprecise."""

    title = 'date is imprecise'
    parameter_name = 'date_is_imprecise'

    def queryset(self, request, queryset):
        """Returns the queryset filtered by whether dates are imprecise."""
        if self.value() == YES:
            return queryset.filter(date__second='01', date__minute='01', date__hour='01')
        return queryset


class TypeFilter(SimpleListFilter):
    """Filters sources by type."""

    title = 'type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        return Source.get_meta().get_field('type').choices

    def queryset(self, request, queryset):
        """Returns the queryset filtered by type."""
        type_value = self.value()
        if not type_value:
            return queryset
        return queryset.filter(type=type_value)
