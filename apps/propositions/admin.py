from apps.admin.admin_site import admin_site
from apps.admin.inlines import TabularInline
from apps.entities.admin.filters import RelatedEntityFilter
from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.propositions import models
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.citations import AbstractSourcesInline
from apps.topics.admin.related_topics import AbstractRelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter


class RelatedTopicsInline(AbstractRelatedTopicsInline):
    """Inline admin for topic tags."""

    model = models.TypedProposition.tags.through


class SourcesInline(AbstractSourcesInline):
    """Inline admin for sources."""

    model = models.TypedProposition.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for related entities."""

    model = models.TypedProposition.related_entities.through


class ConclusionsInline(TabularInline):
    """Inline admin for a proposition's supported propositions."""

    verbose_name = 'supported proposition'
    verbose_name_plural = 'supported propositions'
    model = models.Support
    exclude = ['position']
    fk_name = 'premise'
    autocomplete_fields = ['conclusion']
    extra = 0


class PremisesInline(TabularInline):
    """Inline admin for a proposition's premises."""

    verbose_name = 'premise'
    verbose_name_plural = 'premises'
    model = models.Support
    fk_name = 'conclusion'
    autocomplete_fields = ['premise']
    extra = 0

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'


class AbstractPropositionAdmin(SearchableModelAdmin):
    """Abstract base admin for propositions."""

    exclude = SearchableModelAdmin.exclude + [
        'related_entities',
        'sources',
        'images',
        'locations',
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
    list_per_page = 15


class TypedPropositionAdmin(AbstractPropositionAdmin):
    """Admin for all propositions."""

    model = models.TypedProposition

    list_display = AbstractPropositionAdmin.list_display + ['date_html', 'type']
    list_filter = AbstractPropositionAdmin.list_filter + ['type']
    ordering = ['type', 'date']
    search_fields = model.searchable_fields


class PropositionAdmin(AbstractPropositionAdmin):
    """Admin for propositions."""


admin_site.register(models.TypedProposition, TypedPropositionAdmin)
admin_site.register(models.Proposition, PropositionAdmin)
