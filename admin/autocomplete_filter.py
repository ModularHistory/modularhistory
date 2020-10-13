"""AutocompleteFilter based on https://github.com/farhan0581/django-admin-autocomplete-filter."""

import re
from typing import Any, Type

from admin_auto_filters.filters import AutocompleteFilter as BaseAutocompleteFilter, AutocompleteSelect
from django.core.exceptions import FieldDoesNotExist
from django.utils.html import SafeString, format_html

from modularhistory.models import Model


class AutocompleteFilter(BaseAutocompleteFilter):
    """TODO: add docstring."""

    rendered_widget: SafeString


class ManyToManyAutocompleteFilter(AutocompleteFilter):
    """Autocomplete filter for many2many fields."""

    _parameter_name: str
    m2m_cls: Type[Model]

    def __init__(self, request, params, model, model_admin):
        """TODO: add docstring."""
        try:
            super().__init__(request, params, model, model_admin)
        except FieldDoesNotExist:
            raise
        if self.value():
            obj = self.m2m_cls.objects.get(pk=self.value())
            rendered_widget = re.sub(r'(selected>).+(</option>)', rf'\g<1>{obj}\g<2>', self.rendered_widget)
            self.rendered_widget = format_html(rendered_widget)

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value():
            return queryset.filter(**{self._parameter_name: self.value()})
        return queryset
