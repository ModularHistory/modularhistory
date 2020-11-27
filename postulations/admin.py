from admin import ModelAdmin, StackedInline, TabularInline, admin_site
from entities.admin.admin_filters import EntityAutocompleteFilter
from postulations import models


class FactEntitiesInline(TabularInline):
    """Inline admin for a fact's related entities."""

    model = models.Postulation.related_entities.through
    extra = 0


class OccurrencesInline(TabularInline):
    """Inline admin for a fact's related occurences."""

    model = models.Postulation.related_occurrences.through
    extra = 0


class SupportedFactsInline(StackedInline):
    """Inline admin for a fact's supported postulations."""

    verbose_name = 'supported fact'
    verbose_name_plural = 'supported postulations'
    model = models.PostulationSupport
    fk_name = 'supportive_fact'
    extra = 0


class SupportiveFactsInline(StackedInline):
    """Inline admin for a postulation's supportive facts."""

    verbose_name = 'supportive fact'
    verbose_name_plural = 'supportive facts'
    model = models.PostulationSupport
    fk_name = 'supported_fact'
    extra = 0


class FactAdmin(ModelAdmin):
    """Admin for postulations."""

    model = models.Postulation
    list_display = ['pk', 'summary']
    list_filter = ['related_entities', 'related_occurrences']
    search_fields = model.searchable_fields

    inlines = [
        FactEntitiesInline,
        OccurrencesInline,
        SupportedFactsInline,
        SupportiveFactsInline,
    ]


admin_site.register(models.Postulation, FactAdmin)
