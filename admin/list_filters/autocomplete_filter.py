"""AutocompleteFilter based on https://github.com/farhan0581/django-admin-autocomplete-filter."""

import re
from typing import Type

from admin_auto_filters.filters import AutocompleteFilter as BaseAutocompleteFilter
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.models import Model


class AutocompleteFilter(BaseAutocompleteFilter):
    """TODO: add docstring."""

    rendered_widget: SafeString


class ManyToManyAutocompleteFilter(AutocompleteFilter):
    """Autocomplete filter for many2many fields."""

    _parameter_name: str
    m2m_cls: Type[Model]

    def __init__(self, request, query_params, model, model_admin):
        """TODO: add docstring."""
        super().__init__(request, query_params, model, model_admin)
        if self.value():
            model_instance = self.m2m_cls.objects.get(pk=self.value())
            rendered_widget = re.sub(
                r'(selected>).+(</option>)',
                rf'\g<1>{model_instance}\g<2>',
                self.rendered_widget
            )
            self.rendered_widget = format_html(rendered_widget)

    @property
    def key(self) -> str:
        """Returns an identifier for the filter."""
        # Use `title` since `parameter_name` might have an unwanted plural form
        # if the field is m2m.
        return self.title.replace(' ', '_')

    def get_autocomplete_url(self, request, model_admin) -> str:
        """Returns the URL used by the autocomplete filter."""
        return reverse(f'admin:{self.key}_search')

    def queryset(self, request, queryset) -> 'QuerySet[Model]':
        """Returns the filtered queryset."""
        if self.value():
            return queryset.filter(**{self._parameter_name: self.value()})
        return queryset
