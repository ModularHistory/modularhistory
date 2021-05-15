from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from apps.admin import StackedInline, TabularInline, admin_site
from apps.admin.list_filters.type_filter import PolymorphicContentTypeFilter
from apps.entities.admin.filters import RelatedEntityFilter
from apps.occurrences.models.occurrence import Occurrence
from apps.propositions import models
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin import CitationsInline
from apps.topics.admin import RelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter


class RelatedEntitiesInline(TabularInline):
    """Inline admin for related entities."""

    model = models.Proposition.related_entities.through
    extra = 0
    show_change_link = True
    autocomplete_fields = ['entity']
    verbose_name = 'related entity'
    verbose_name_plural = 'related entities'


class ConclusionsInline(StackedInline):
    """Inline admin for a proposition's supported propositions."""

    verbose_name = 'supported proposition'
    verbose_name_plural = 'supported propositions'
    model = models.Support
    fk_name = 'premise'
    autocomplete_fields = ['conclusion']
    extra = 0


class PremisesInline(StackedInline):
    """Inline admin for a proposition's premises."""

    verbose_name = 'premise'
    verbose_name_plural = 'premises'
    model = models.Support
    fk_name = 'conclusion'
    extra = 0


class PolymorphicPropositionAdmin(PolymorphicParentModelAdmin, SearchableModelAdmin):
    """Admin for propositions."""

    base_model = models.Proposition
    child_models = (models.Proposition, Occurrence)

    model = models.Proposition
    list_display = ['summary', 'slug', 'tags_string', 'ctype_name']
    list_filter = [
        PolymorphicContentTypeFilter,
        TopicFilter,
        RelatedEntityFilter,
    ]
    search_fields = model.searchable_fields


class PropositionChildAdmin(PolymorphicChildModelAdmin, SearchableModelAdmin):
    """Admin for models that inherit from `Proposition`."""

    base_model = models.Proposition

    model = models.Proposition
    exclude = ['related_entities']
    inlines = [
        CitationsInline,
        ConclusionsInline,
        PremisesInline,
        RelatedEntitiesInline,
        RelatedTopicsInline,
    ]
    list_display = ['summary', 'slug', 'tags_string', 'ctype_name']
    list_filter = [
        PolymorphicContentTypeFilter,
        TopicFilter,
        RelatedEntityFilter,
    ]
    search_fields = model.searchable_fields


admin_site.register(models.Proposition, PropositionChildAdmin)
