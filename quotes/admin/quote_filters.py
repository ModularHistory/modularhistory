# TODO: stop ignoring types when mypy bug is fixed

import re

from admin_auto_filters.filters import AutocompleteSelect
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from admin.autocomplete_filter import BaseAutocompleteFilter, ManyToManyAutocompleteFilter
from entities.models import Category, Entity


class AttributeeFilter(ManyToManyAutocompleteFilter):
    """TODO: add docstring."""

    title = 'attributee'
    field_name = 'attributees'

    _parameter_name = 'attributees__pk__exact'
    m2m_cls = Entity

    def get_autocomplete_url(self, request, model_admin):
        """TODO: add docstring."""
        return reverse('admin:attributee_search')


class AttributeeCategoryFilter(ManyToManyAutocompleteFilter):
    """TODO: add docstring."""

    title = 'attributee categories'
    field_name = 'attributee_categories'

    _parameter_name = 'attributees__categories__pk__exact'
    _rel = Entity.categories.through.get_meta().get_field('category').remote_field
    m2m_cls = Category

    def get_autocomplete_url(self, request, model_admin):
        """TODO: add docstring."""
        return reverse('admin:entity_category_search')

    def __init__(self, request, params, model, model_admin):
        """TODO: add docstring."""
        try:
            super().__init__(request, params, model, model_admin)
        except FieldDoesNotExist:
            if self.parameter_name is None:
                self.parameter_name = self.field_name
                if self.use_pk_exact:
                    self.parameter_name = f'{self.parameter_name}__{self.field_pk}__exact'
            super(BaseAutocompleteFilter, self).__init__(request, params, model, model_admin)
            if self.rel_model:
                model = self.rel_model
            widget = AutocompleteSelect(
                self._rel,
                model_admin.admin_site,
                custom_url=self.get_autocomplete_url(request, model_admin)
            )
            form_field = self.get_form_field()
            field = form_field(
                queryset=self.get_queryset_for_field(model, self.field_name),
                widget=widget,
                required=False,
            )
            self._add_media(model_admin, widget)
            attrs = self.widget_attrs.copy()
            attrs['id'] = f'id-{self.parameter_name}-dal-filter'
            if self.is_placeholder_title:
                # Use upper-case letter P as a dirty hack
                attrs['data-Placeholder'] = self.title
            self.rendered_widget = field.widget.render(
                name=self.parameter_name,
                value=self.used_parameters.get(self.parameter_name, ''),
                attrs=attrs
            )
        if self.value():
            print('There is a value!!!!')
            obj = self.m2m_cls.objects.get(pk=self.value())
            rendered_widget = re.sub(r'(selected>).+(</option>)', rf'\g<1>{obj}\g<2>', self.rendered_widget)
            self.rendered_widget = format_html(rendered_widget)

    def get_queryset_for_field(self, model, name):
        """Override."""
        return self.m2m_cls.objects.all()


class HasSourceFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has source'
    parameter_name = 'has_source'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.exclude(sources=None)
        if self.value() == 'No':
            return queryset.filter(sources=None)


class AttributeeCountFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'attributee count'
    parameter_name = 'attributee_count'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4+'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        queryset = queryset.annotate(attributee_count=Count('attributees'))
        try:
            n = int(self.value())
        except TypeError:  # `All`
            return queryset
        if n == 4:
            return queryset.exclude(attributee_count__lt=n)
        return queryset.filter(attributee_count=n)


class HasMultipleCitationsFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has multiple citations'
    parameter_name = 'has_multiple_citations'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        queryset = queryset.annotate(citation_count=Count('citations'))
        if self.value() == 'Yes':
            return queryset.exclude(citation_count__lt=2)
        if self.value() == 'No':
            return queryset.filter(citation_count__gte=2)
