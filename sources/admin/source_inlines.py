from typing import Optional

from admin.admin import GenericTabularInline, TabularInline
from sources import models
from sources.models import Source


class AttributeesInline(TabularInline):
    """TODO: add docstring."""

    model = Source.attributees.through
    autocomplete_fields = ['attributee']

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(self, request, obj: Optional[Source] = None, **kwargs):
        """TODO: add docstring."""
        if obj:
            if obj.attributees.count():
                return 0
        return 1


class ContainersInline(TabularInline):
    """TODO: add docstring."""

    verbose_name = 'container'
    verbose_name_plural = 'containers'
    model = Source.containers.through
    fk_name = 'source'
    extra = 0
    autocomplete_fields = ['container']


class ContainedSourcesInline(TabularInline):
    """TODO: add docstring."""

    verbose_name = 'contained source'
    verbose_name_plural = 'contained sources'
    model = Source.containers.through
    fk_name = 'container'
    extra = 0
    autocomplete_fields = ['source']


class RelatedInline(GenericTabularInline):
    """TODO: add docstring."""

    model = models.Citation
    extra = 0
    verbose_name = 'related obj'
    verbose_name_plural = 'related objects (not yet implemented)'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'