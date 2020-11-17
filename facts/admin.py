from admin import ModelAdmin, StackedInline, TabularInline, admin_site
from facts import models


class FactEntitiesInline(TabularInline):
    """Inline admin for a fact's related entities."""

    model = models.Fact.related_entities.through
    extra = 0


class OccurrencesInline(TabularInline):
    """Inline admin for a fact's related occurences."""

    model = models.Fact.related_occurrences.through
    extra = 0


class SupportedFactsInline(StackedInline):
    """Inline admin for a fact's supported facts."""

    verbose_name = 'supported fact'
    verbose_name_plural = 'supported facts'
    model = models.FactSupport
    fk_name = 'supported_fact'
    extra = 0


class SupportiveFactsInline(StackedInline):
    """Inline admin for a fact's supportive facts."""

    verbose_name = 'supportive fact'
    verbose_name_plural = 'supportive facts'
    model = models.FactSupport
    fk_name = 'supportive_fact'
    extra = 0


class FactAdmin(ModelAdmin):
    """Admin for facts."""

    model = models.Fact
    list_display = ['pk', 'summary']
    list_filter = ['related_entities', 'related_occurrences']
    search_fields = model.searchable_fields

    inlines = [
        FactEntitiesInline,
        OccurrencesInline,
        SupportedFactsInline,
        SupportiveFactsInline,
    ]


admin_site.register(models.Fact, FactAdmin)
