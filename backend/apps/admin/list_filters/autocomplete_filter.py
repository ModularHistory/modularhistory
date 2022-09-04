"""AutocompleteFilter based on https://github.com/farhan0581/django-admin-autocomplete-filter."""

import re
from typing import TYPE_CHECKING, Union

from admin_auto_filters.filters import AutocompleteFilter as BaseAutocompleteFilter
from django.apps import apps
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from core.models.model import ExtendedModel

if TYPE_CHECKING:
    from django.http import HttpRequest


# https://github.com/farhan0581/django-admin-autocomplete-filter
class AutocompleteFilter(BaseAutocompleteFilter):
    """Wraps admin_auto_filters.filters.AutocompleteFilter."""

    rendered_widget: SafeString


class ManyToManyAutocompleteFilter(AutocompleteFilter):
    """Autocomplete filter to be used with many-to-many relationships."""

    m2m_cls: Union[type['ExtendedModel'], str]

    def __init__(self, request: 'HttpRequest', query_params, model, model_admin):
        """Construct the many-to-many autocomplete filter."""
        super().__init__(request, query_params, model, model_admin)
        m2m_cls: type['ExtendedModel']
        if isinstance(self.m2m_cls, str):
            m2m_cls = apps.get_model(*(self.m2m_cls.split('.')))
        else:
            m2m_cls = self.m2m_cls
        if self.value():
            model_instance = m2m_cls.objects.get(pk=self.value())
            rendered_widget = re.sub(
                r'(selected>).+(</option>)',
                rf'\g<1>{model_instance}\g<2>',
                self.rendered_widget,
            )
            self.rendered_widget = format_html(rendered_widget)

    @property
    def key(self) -> str:
        """Return an identifier for the filter."""
        # Use `title` since `parameter_name` might have an unwanted plural form
        # if the field is m2m.
        return self.title.replace(' ', '_')

    def get_autocomplete_url(self, request: 'HttpRequest', model_admin) -> str:
        """Return the URL used by the autocomplete filter."""
        return reverse(f'admin:{self.key}_search')

    def queryset(
        self, request: 'HttpRequest', queryset: 'QuerySet[ExtendedModel]'
    ) -> 'QuerySet[ExtendedModel]':
        """Return the filtered queryset."""
        if self.value():
            return queryset.filter(**{self._parameter_name: self.value()})
        return queryset

    @property
    def _parameter_name(self) -> str:
        return f'{self.field_name}__pk__exact'
