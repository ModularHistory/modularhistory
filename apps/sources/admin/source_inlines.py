from admin import GenericTabularInline, TabularInline
from apps.sources import models
from apps.sources.models import Source


class AttributeesInline(TabularInline):
    """Inline admin for a source's attributees."""

    model = Source.attributees.through
    autocomplete_fields = ['attributee']

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'


class ContainersInline(TabularInline):
    """Inline admin for a source's containers."""

    verbose_name = 'container'
    verbose_name_plural = 'containers'
    model = Source.containers.through
    fk_name = 'source'
    extra = 0
    autocomplete_fields = ['container']


class ContainedSourcesInline(TabularInline):
    """Inline admin for a source's contained sources."""

    verbose_name = 'contained source'
    verbose_name_plural = 'contained sources'
    model = Source.containers.through
    fk_name = 'container'
    extra = 0
    autocomplete_fields = ['source']


class RelatedInline(GenericTabularInline):
    """Inline admin for a source's related objects."""

    model = models.Citation
    extra = 0
    verbose_name = 'related obj'
    verbose_name_plural = 'related objects (not yet implemented)'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'
