from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from apps.admin import StackedInline, admin_site
from apps.admin.list_filters.type_filter import PolymorphicContentTypeFilter
from apps.entities.admin.filters import RelatedEntityFilter
from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.occurrences.models.occurrence import NewOccurrence as Occurrence
from apps.propositions import models
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.citations import AbstractSourcesInline
from apps.topics.admin.related_topics import AbstractRelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter


class RelatedTopicsInline(AbstractRelatedTopicsInline):
    """Inline admin for topic tags."""

    model = models.Proposition.tags.through


class SourcesInline(AbstractSourcesInline):
    """Inline admin for sources."""

    model = models.Proposition.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for related entities."""

    model = models.Proposition.related_entities.through


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


class PropositionTypeFilter(PolymorphicContentTypeFilter):
    model_options = [models.Proposition, Occurrence]


class AbstractPropositionAdmin(SearchableModelAdmin):
    """Abstract base admin for propositions."""

    exclude = SearchableModelAdmin.exclude + [
        'related_entities',
        'citations',
        'sources',
    ]
    inlines = [
        PremisesInline,
        ConclusionsInline,
        SourcesInline,
        RelatedEntitiesInline,
        RelatedTopicsInline,
    ]
    list_display = [
        'slug',
        'summary',
        'tags_string',
    ]
    list_filter = [
        TopicFilter,
        RelatedEntityFilter,
    ]


class PolymorphicPropositionAdmin(
    PolymorphicParentModelAdmin, AbstractPropositionAdmin
):
    """Admin for propositions."""

    base_model = models.Proposition
    child_models = (models.Proposition, Occurrence)

    model = models.Proposition

    list_display = AbstractPropositionAdmin.list_display + ['ctype_name']
    list_filter = AbstractPropositionAdmin.list_filter + [PropositionTypeFilter]
    search_fields = model.searchable_fields

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('polymorphic_ctype')


class PropositionChildAdmin(PolymorphicChildModelAdmin, AbstractPropositionAdmin):
    """Admin for models that inherit from `Proposition`."""

    base_model = models.Proposition

    model = models.Proposition
    exclude = AbstractPropositionAdmin.exclude
    search_fields = model.searchable_fields


admin_site.register(models.Proposition, PolymorphicPropositionAdmin)
