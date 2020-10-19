"""AutocompleteFilter based on https://github.com/farhan0581/django-admin-autocomplete-filter."""

import re
from typing import Type

from admin_auto_filters.filters import AutocompleteFilter as BaseAutocompleteFilter
from django.utils.safestring import SafeString
from django.utils.html import format_html

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

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value():
            return queryset.filter(**{self._parameter_name: self.value()})
        return queryset
