import re
from typing import Optional

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from admin.autocomplete_filter import AutocompleteFilter
from entities.models import Entity


class AttributeeFilter(AutocompleteFilter):
    """Autocomplete filter for filtering sources by attributees."""

    title = 'attributee'
    field_name = 'attributees'

    _parameter_name = 'attributees__pk__exact'

    def __init__(self, request, query_params, model, model_admin):
        """TODO: add docstring."""
        super().__init__(request, query_params, model, model_admin)
        rendered_widget: SafeString = self.rendered_widget  # type: ignore
        entity_pk: Optional[int] = self.value()
        if entity_pk:
            attributee: Entity = Entity.objects.get(pk=entity_pk)
            rendered_widget = format_html(
                re.sub(
                    r'(selected>).+(</option>)',
                    rf'\g<1>{attributee}\g<2>',
                    rendered_widget
                )
            )
        self.rendered_widget = rendered_widget

    def get_autocomplete_url(self, request, model_admin):
        """Returns the filter's autocomplete URL."""
        return reverse('admin:attributee_search')

    def queryset(self, request, queryset):
        """Returns the filtered queryset."""
        if self.value():
            return queryset.filter(**{self._parameter_name: self.value()})
        return queryset
