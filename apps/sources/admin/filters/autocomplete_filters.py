from apps.entities.admin.filters import EntityAutocompleteFilter


class AttributeeFilter(EntityAutocompleteFilter):
    """Autocomplete filter for filtering sources by attributees."""

    title = 'attributee'
    field_name = 'attributees'
