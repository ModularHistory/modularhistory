from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter


class ClassificationFilter(AutocompleteFilter):
    title = 'Classification'
    field_name = 'classifications'


class HasQuotesFilter(SimpleListFilter):
    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.exclude(quotes=None)
        elif value == 'No':
            return queryset.filter(quotes=None)
        return queryset


class HasImageFilter(SimpleListFilter):
    title = 'has image'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.exclude(images=None)
        elif value == 'No':
            return queryset.filter(images=None)
        return queryset
