from admin.admin import admin_site, Admin, TabularInline, StackedInline
from topics import models


class FactEntitiesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Fact.related_entities.through
    extra = 1


# class FactTopicsInline(TabularInline):
#     model = models.Fact.related_topics.through
#     extra = 1


class OccurrencesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Fact.related_occurrences.through
    extra = 1


class SupportedFactsInline(StackedInline):
    """TODO: add docstring."""

    model = models.FactSupport
    fk_name = 'supported_fact'
    extra = 1


class SupportiveFactsInline(StackedInline):
    """TODO: add docstring."""

    model = models.FactSupport
    fk_name = 'supportive_fact'
    extra = 1


class FactAdmin(Admin):
    """TODO: add docstring."""

    list_display = ['text']
    list_filter = ['related_entities', 'related_occurrences']
    search_fields = ['text']
    # ordering = ['datetime', 'start_date', 'end_date']

    inlines = [
        FactEntitiesInline,
        # FactTopicsInline,
        OccurrencesInline,
        SupportedFactsInline,
        SupportiveFactsInline
    ]


admin_site.register(models.Fact, FactAdmin)
