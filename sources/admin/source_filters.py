from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from sources.models import Source


class HasContainerFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has container'
    parameter_name = 'has_container'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.exclude(containers=None)
        if self.value() == 'No':
            return queryset.filter(containers=None)


class HasFileFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has file'
    parameter_name = 'has_file'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.filter(db_file__isnull=False).exclude(db_file__file='')
        if self.value() == 'No':
            return queryset.filter(Q(db_file__isnull=True) | Q(db_file__file=''))


class HasPageNumber(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has page number'
    parameter_name = 'has_page_number'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        queryset = queryset.filter(db_file__isnull=False).exclude(db_file__file='')
        ids = []
        for source in queryset:
            source_object = getattr(source, 'obj', None) or source
            if hasattr(source_object, 'page_number'):
                has_page_number = bool(source_object.page_number)
                if self.value() == 'Yes':
                    include_object = has_page_number
                elif self.value() == 'No':
                    include_object = not has_page_number
                else:
                    include_object = True
                if include_object:
                    ids.append(source.id)
        return queryset.filter(id__in=ids)


class HasFilePageOffsetFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has file page offset'
    parameter_name = 'has_file_page_offset'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        sources_with_files = queryset.filter(db_file__isnull=False).exclude(db_file__file='')
        ids = []
        if self.value() == 'Yes':
            for source in sources_with_files:
                file = source.file
                if file.page_offset:
                    ids.append(source.id)
            return sources_with_files.filter(id__in=ids)
        elif self.value() == 'No':
            for source in sources_with_files:
                file = source.file
                if not file.page_offset:
                    ids.append(source.id)
            return sources_with_files.filter(id__in=ids)


class ImpreciseDateFilter(SimpleListFilter):
    """TODO: add docstring."""
    title = 'date is imprecise'
    parameter_name = 'date_is_imprecise'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            # ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.filter(date__second='01', date__minute='01', date__hour='01')
        return queryset


class TypeFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'content type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        type_labels = Source.objects.all().values('type').distinct()
        return [(f'{type_label}', f'{type_label}') for type_label in type_labels]

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        value = self.value()
        if not value:
            return queryset
        if '.' in value:
            # app_name, model_name = value.split('.')
            return queryset.filter(type=value)
        return queryset
