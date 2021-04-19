from typing import TYPE_CHECKING, Type

from django.contrib.admin import SimpleListFilter
from polymorphic.admin import PolymorphicParentModelAdmin

if TYPE_CHECKING:
    from polymorphic.models import PolymorphicModel

    from core.models import TypedModel


class PolymorphicContentTypeFilter(SimpleListFilter):
    """Filters sources by type."""

    title = 'content type'
    parameter_name = 'polymorphic_ctype_id'
    base_model: Type['PolymorphicModel']

    def lookups(self, request, model_admin: PolymorphicParentModelAdmin):
        """Return an iterable of tuples (value, verbose value)."""
        return sorted(
            {
                (instance.polymorphic_ctype_id, instance.ctype_name)
                for instance in model_admin.get_queryset(request)
            },
            key=lambda ctype_tuple: ctype_tuple[1],
        )

    def queryset(self, request, queryset):
        """Return the queryset filtered by type."""
        content_type_id = self.value()
        if not content_type_id:
            return queryset
        return queryset.filter(**{self.parameter_name: content_type_id})


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
