from django.urls import path

from apps.admin import TabularInline, admin_site
from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.admin.list_filters.boolean_filters import HasRelationFilter
from apps.moderation.admin.moderated_model.admin import ModeratedModelAdmin
from apps.topics import models
from apps.topics.views import TagSearchView


class TopicRelationsInline(TabularInline):
    """Inline admin for a topic's related topics."""

    model = models.Topic.related_topics.through
    fk_name = 'topic'
    autocomplete_fields = ['related_topic']
    extra = 1
    verbose_name_plural = 'related topics'
    verbose_name = 'related topic'


class ChildTopicsInline(TabularInline):
    """Inline admin for a topic's child topics."""

    model = models.TopicEdge
    fk_name = 'parent'
    autocomplete_fields = ['child']
    extra = 1
    verbose_name = 'child topic'
    verbose_name_plural = 'child topics'


class ParentTopicsInline(TabularInline):
    """Inline admin for a topic's parent topics."""

    model = models.TopicEdge
    fk_name = 'child'
    autocomplete_fields = ['parent']
    extra = 1
    verbose_name = 'parent topic'
    verbose_name_plural = 'parent topics'


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

    inlines = [
        ParentTopicsInline,
        ChildTopicsInline,
        TopicRelationsInline,
    ]
    exclude = ['key', 'cache', 'related_topics', 'children']
    list_display = [
        'name',
        'aliases',
        'slug',
        'detail_link',
        'tags_string',
    ]
    list_filter = [RelatedTopicFilter, HasParentFilter]
    list_per_page = 25
    ordering = ['name']
    search_fields = [
        'name',
        'aliases',
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
