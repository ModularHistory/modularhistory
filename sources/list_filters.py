from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class HasFileFilter(SimpleListFilter):
    title = 'has file'
    parameter_name = 'has_file'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(file__isnull=False).exclude(file__file='')
        if self.value() == 'No':
            return queryset.filter(Q(file__isnull=True) | Q(file__file=''))


class HasPageNumber(SimpleListFilter):
    title = 'has page number'
    parameter_name = 'has_page_number'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.filter(file__isnull=False).exclude(file__file='')
        ids = []
        if self.value() == 'Yes':
            for source in queryset:
                obj = source.object if hasattr(source, 'object') else source
                if hasattr(obj, 'page_number'):
                    if obj.page_number:
                        ids.append(source.id)
            return queryset.filter(id__in=ids)
        if self.value() == 'No':
            for source in queryset:
                obj = source.object if hasattr(source, 'object') else source
                if hasattr(obj, 'page_number'):
                    if not obj.page_number:
                        ids.append(source.id)
            return queryset.filter(id__in=ids)


class HasFilePageOffsetFilter(SimpleListFilter):
    title = 'has file page offset'
    parameter_name = 'has_file_page_offset'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        sources_with_files = queryset.filter(file__isnull=False).exclude(file__file='')
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
    title = 'date is imprecise'
    parameter_name = 'date_is_imprecise'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            # ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(date__second='01', date__minute='01', date__hour='01')
        return queryset
