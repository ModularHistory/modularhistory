import re

from admin_auto_filters.filters import AutocompleteSelect
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from apps.admin.list_filters.autocomplete_filter import (
    BaseAutocompleteFilter,
    ManyToManyAutocompleteFilter,
)
from apps.entities.admin.filters import EntityAutocompleteFilter
from apps.entities.models import Category, Entity


class AttributeeFilter(EntityAutocompleteFilter):
    """Autocomplete filter for a quote's attributees."""

    title = 'attributee'
    field_name = 'attributees'


class AttributeeCategoryFilter(ManyToManyAutocompleteFilter):
    """Autocomplete filter for a quote's attributee's categorization."""

    title = 'attributee categories'
    field_name = 'attributee_categories'

    _parameter_name = 'attributees__categories__pk__exact'
    _rel = Entity.categories.through._meta.get_field('category').remote_field
    m2m_cls = Category

    def __init__(self, request, query_params, model, model_admin):
        """Return the URL associated with the autocomplete view."""
        try:
            super().__init__(request, query_params, model, model_admin)
        except FieldDoesNotExist:
            if self.parameter_name is None:
                self.parameter_name = self.field_name
                if self.use_pk_exact:
                    self.parameter_name = f'{self.parameter_name}__{self.field_pk}__exact'
            super(BaseAutocompleteFilter, self).__init__(
                request, query_params, model, model_admin
            )
            if self.rel_model:
                model = self.rel_model
            widget = AutocompleteSelect(
                self._rel,
                model_admin.admin_site,
                custom_url=self.get_autocomplete_url(request, model_admin),
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
                attrs=attrs,
            )
        if self.value():
            model_instance = self.m2m_cls.objects.get(pk=self.value())
            rendered_widget = re.sub(
                r'(selected>).+(</option>)',
                rf'\g<1>{model_instance}\g<2>',
                self.rendered_widget,
            )
            self.rendered_widget = format_html(rendered_widget)

    def get_autocomplete_url(self, request, model_admin):
        """Return the URL associated with the autocomplete view."""
        return reverse('admin:entity_category_search')

    def get_queryset_for_field(self, model, name):
        """Override."""
        return self.m2m_cls.objects.all()


class AttributeeCountFilter(SimpleListFilter):
    """Filter for number of attributees."""

    title = 'attributee count'
    parameter_name = 'attributee_count'

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return (
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4+'),
        )

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        queryset = queryset.annotate(attributee_count=Count('attributees'))
        try:
            attributee_count = int(self.value())
        except TypeError:  # `All`
            return queryset
        if attributee_count == 4:
            return queryset.exclude(attributee_count__lt=attributee_count)
        return queryset.filter(attributee_count=attributee_count)
