from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter


class CategoriesFilter(AutocompleteFilter):
    """TODO: add docstring."""

    title = 'Categories'
    field_name = 'categories'


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
        value = self.value()
        if value == 'Yes':
            return queryset.exclude(quotes=None)
        elif value == 'No':
            return queryset.filter(quotes=None)
        return queryset


class HasImageFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has image'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        value = self.value()
        if value == 'Yes':
            return queryset.exclude(images=None)
        elif value == 'No':
            return queryset.filter(images=None)
        return queryset
