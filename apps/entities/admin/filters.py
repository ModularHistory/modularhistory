"""List filters for the entities admin."""

from django.urls import reverse

from apps.admin.list_filters import (
    AutocompleteFilter,
    BooleanListFilter,
    ManyToManyAutocompleteFilter,
    TypeFilter,
)
from apps.entities.models.entity import Entity
from core.constants.strings import NO, YES


class CategoriesFilter(AutocompleteFilter):
    """Admin filter for entities' categories."""

    title = 'Categories'
    field_name = 'categories'


class HasQuotesFilter(BooleanListFilter):
    """Admin filter for whether entities have quotes."""

    title = 'has quotes'
    parameter_name = 'has_quotes'

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        option = self.value()
        if option == YES:
            return queryset.exclude(quotes=None)
        elif option == NO:
            return queryset.filter(quotes=None)
        return queryset


class HasImageFilter(BooleanListFilter):
    """Admin filter for whether entities have images."""

    title = 'has image'
    parameter_name = 'has_image'

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        option = self.value()
        if option == YES:
            return queryset.exclude(images=None)
        elif option == NO:
            return queryset.filter(images=None)
        return queryset


class EntityTypeFilter(TypeFilter):
    """Admin filter for type of entity."""

    base_model = Entity


class EntityAutocompleteFilter(ManyToManyAutocompleteFilter):
    """Autocomplete filter for a quote's attributees."""

    title: str
    field_name: str
    m2m_cls = Entity

    def get_autocomplete_url(self, request, model_admin):
        """Return the URL of the autocomplete view."""
        return reverse('admin:entity_search')


class RelatedEntityFilter(EntityAutocompleteFilter):
    """Autocomplete filter for related entities."""

    title = 'related entity'
    field_name = 'related_entities'
