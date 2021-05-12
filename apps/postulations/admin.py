from apps.admin import ModelAdmin, StackedInline, admin_site
from apps.postulations import models
from apps.sources.admin import CitationsInline
from apps.topics.admin import RelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter


class SupportedPostulationsInline(StackedInline):
    """Inline admin for a postulation's supported postulations."""

    verbose_name = 'supported postulation'
    verbose_name_plural = 'supported postulations'
    model = models.PostulationSupport
    fk_name = 'supportive_postulation'
    autocomplete_fields = ['supported_postulation']
    extra = 0


class SupportivePostulationsInline(StackedInline):
    """Inline admin for a postulation's supportive postulations."""

    verbose_name = 'supportive postulation'
    verbose_name_plural = 'supportive postulations'
    model = models.PostulationSupport
    fk_name = 'supported_postulation'
    extra = 0


class PostulationAdmin(ModelAdmin):
    """Admin for postulations."""

    model = models.Postulation
    list_display = ['summary', 'slug', 'tags_string']
    list_filter = [TopicFilter, 'related_entities', 'occurrence_set']
    search_fields = model.searchable_fields

    inlines = [
        CitationsInline,
        SupportedPostulationsInline,
        SupportivePostulationsInline,
        RelatedTopicsInline,
    ]


admin_site.register(models.Postulation, PostulationAdmin)
