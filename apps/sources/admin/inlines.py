from apps.admin import TabularInline
from apps.sources.models.source import Source


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
