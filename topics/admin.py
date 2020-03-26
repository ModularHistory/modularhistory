
from admin import admin_site, Admin, TabularInline, StackedInline
from . import models


class RelatedOccurrencesInline(TabularInline):
    model = models.Topic.related_occurrences.through
    extra = 1


class RelatedTopicsInline(TabularInline):
    model = models.Topic.related_topics2.through
    fk_name = 'from_topic'
    autocomplete_fields = ['to_topic']
    extra = 1


class ParentTopicsInline(TabularInline):
    model = models.Topic.parent_topics.through
    fk_name = 'child_topic'
    autocomplete_fields = ['parent_topic']
    extra = 1


class ChildTopicsInline(TabularInline):
    model = models.Topic.parent_topics.through
    fk_name = 'parent_topic'
    autocomplete_fields = ['child_topic']
    extra = 1


class TopicAdmin(Admin):
    list_display = (
        'key',
        'detail_link',
        'description',
        'parent_topics_string',
        'child_topics_string',
        'related_topics_string'
    )
    list_filter = ('related_topics',)
    search_fields = ('key', 'aliases', 'description')
    ordering = ('key',)

    inlines = [
        ParentTopicsInline,
        ChildTopicsInline,
        RelatedTopicsInline,
        RelatedOccurrencesInline,
    ]


class FactEntitiesInline(TabularInline):
    model = models.Fact.related_entities.through
    extra = 1


class FactTopicsInline(TabularInline):
    model = models.Fact.related_topics.through
    extra = 1


class OccurrencesInline(TabularInline):
    model = models.Fact.related_occurrences.through
    extra = 1


class SourcesInline(StackedInline):
    model = models.Fact.sources.through
    extra = 1


class SupportedFactsInline(StackedInline):
    model = models.FactSupport
    fk_name = 'supported_fact'
    extra = 1


class SupportiveFactsInline(StackedInline):
    model = models.FactSupport
    fk_name = 'supportive_fact'
    extra = 1


class FactAdmin(Admin):
    list_display = ('text',)
    list_filter = ('related_topics', 'related_entities', 'related_occurrences')
    search_fields = ('text',)
    # ordering = ('datetime', 'start_date', 'end_date')

    inlines = [
        FactEntitiesInline, FactTopicsInline, OccurrencesInline,
        SourcesInline,
        SupportedFactsInline,
        SupportiveFactsInline
    ]


admin_site.register(models.Topic, TopicAdmin)
admin_site.register(models.Fact, FactAdmin)
