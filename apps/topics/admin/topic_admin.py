from django.urls import path

from apps.admin import ModelAdmin, admin_site
from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.topics import models
from apps.topics.admin.topic_inlines import (
    ChildTopicsInline,
    ParentTopicsInline,
    TopicRelationsInline,
)
from apps.topics.views import TagSearchView


class RelatedTopicFilter(ManyToManyAutocompleteFilter):
    """Filter topic list by a related topic."""

    title = 'related topic'
    field_name = 'related_topics'
    _parameter_name = 'related_topics__pk__exact'
    m2m_cls = models.Topic


class TopicAdmin(ModelAdmin):
    """Admin for topics."""

    model = models.Topic

    autocomplete_fields = ['parent']
    inlines = [
        ParentTopicsInline,
        ChildTopicsInline,
        TopicRelationsInline,
        # RelatedOccurrencesInline,
    ]
    exclude = ['key']
    list_display = [
        'name',
        'slug',
        'path',
        'detail_link',
        'parent_topics_string',
        'child_topics_string',
        'tags_string',
    ]
    list_filter = [RelatedTopicFilter]
    list_per_page = 25
    ordering = ['name', 'path']
    readonly_fields = ['pretty_computations', 'path', 'slug']
    search_fields = ['name', 'aliases', 'description']

    def get_urls(self):
        """Return the list of URLs used by the topic admin."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'related_topic_search/',
                self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                name='related_topic_search',
            ),
        ]
        return custom_urls + urls


admin_site.register(models.Topic, TopicAdmin)
