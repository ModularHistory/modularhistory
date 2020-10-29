from django.contrib.admin import SimpleListFilter

from admin.list_filters import AutocompleteFilter
from modularhistory.constants import YES, NO


class CategoriesFilter(AutocompleteFilter):
    """Admin filter for entities' categories."""

    title = 'Categories'
    field_name = 'categories'


class HasQuotesFilter(SimpleListFilter):
    """Admin filter for whether entities have quotes."""

    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        option = self.value()
        if option == YES:
            return queryset.exclude(quotes=None)
        elif option == NO:
            return queryset.filter(quotes=None)
        return queryset


class HasImageFilter(SimpleListFilter):
    """Admin filter for whether entities have images."""

    title = 'has image'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        option = self.value()
        if option == YES:
            return queryset.exclude(images=None)
        elif option == NO:
            return queryset.filter(images=None)
        return queryset
