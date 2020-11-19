from typing import TYPE_CHECKING, Type

from django.contrib.admin import SimpleListFilter

if TYPE_CHECKING:
    from modularhistory.models import TypedModel


class TypeFilter(SimpleListFilter):
    """Filters sources by type."""

    title = 'type'
    parameter_name = 'type'
    base_model: Type['TypedModel']

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return self.base_model.get_meta().get_field('type').choices

    def queryset(self, request, queryset):
        """Return the queryset filtered by type."""
        type_value = self.value()
        if not type_value:
            return queryset
        return queryset.filter(type=type_value)
