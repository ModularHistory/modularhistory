from django.contrib.admin import TabularInline, StackedInline

# from taggit_labels.widgets import LabelWidget
# from taggit.forms import TagField
from admin import admin_site, Admin
from . import models


class RelatedOccurrencesInline(TabularInline):
    model = models.Topic.related_occurrences.through
    extra = 1


class TopicEntitiesInline(TabularInline):
    model = models.Topic.related_entities.through
    extra = 1


class TopicAdmin(Admin):
    list_display = ('key', 'description', 'related_topics_string')
    list_filter = ('related_topics',)
    search_fields = ('key', 'description')
    # ordering = ('datetime', 'start_date', 'end_date')

    inlines = [
        TopicEntitiesInline,
        RelatedOccurrencesInline
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
