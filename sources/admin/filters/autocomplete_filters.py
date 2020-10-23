from django.urls import reverse

from admin.list_filters import ManyToManyAutocompleteFilter


class AttributeeFilter(ManyToManyAutocompleteFilter):
    """Autocomplete filter for filtering sources by attributees."""

    title = 'attributee'
    field_name = 'attributees'
    m2m_cls = 'entities.models.Entity'

    def get_autocomplete_url(self, request, model_admin):
        """Return the URL of the autocomplete view."""
        return reverse('admin:entity_search')
