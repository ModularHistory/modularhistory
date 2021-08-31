from django.urls import path

from apps.admin import admin_site
from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.admin.list_filters.boolean_filters import HasRelationFilter
from apps.moderation.admin.moderated_model.admin import ModeratedModelAdmin
from apps.topics import models
from apps.topics.admin.inlines import TopicRelationsInline
from apps.topics.views import TagSearchView


class RelatedTopicFilter(ManyToManyAutocompleteFilter):
    """Filter the topic list by a related topic."""

    title = 'related topic'
    field_name = 'related_topics'
    _parameter_name = 'related_topics__pk__exact'
    m2m_cls = models.Topic


class HasParentFilter(HasRelationFilter):
    """Filter the topic list by existence of a parent topic."""

    parameter_name = 'has_parent'
    title = 'has parent'
    relation = 'parent'


class TopicAdmin(ModeratedModelAdmin):
    """Admin for topics."""

    model = models.Topic

    autocomplete_fields = ['parent']
    inlines = [
        TopicRelationsInline,
    ]
    exclude = ['key', 'cache', 'related_topics']
    list_display = [
        'name',
        'aliases',
        'slug',
        'path',
        'detail_link',
        'tags_string',
    ]
    list_filter = [RelatedTopicFilter, HasParentFilter]
    list_per_page = 25
    ordering = ['name', 'path']
    readonly_fields = ['path']
    search_fields = [
        'name',
        'aliases',
        'path',
        'description',
    ]

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
