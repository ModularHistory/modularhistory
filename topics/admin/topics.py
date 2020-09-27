from admin.admin import admin_site, Admin, TabularInline
from topics import models


class TopicRelationsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Topic.related_topics.through
    fk_name = 'from_topic'
    autocomplete_fields = ['to_topic']
    extra = 1
    verbose_name_plural = 'related topics'
    verbose_name = 'related topic'


# class RelatedOccurrencesInline(TabularInline):
#     model = models.Topic.related_occurrences.through
#     extra = 1
#     verbose_name_plural = 'related occurrences'
#     verbose_name = 'related occurrence'


class ParentTopicsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Topic.parent_topics.through
    fk_name = 'child_topic'
    autocomplete_fields = ['parent_topic']
    extra = 1
    verbose_name_plural = 'parent topics'
    verbose_name = 'parent topic'


class ChildTopicsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Topic.parent_topics.through
    fk_name = 'parent_topic'
    autocomplete_fields = ['child_topic']
    extra = 1
    verbose_name_plural = 'child topics'
    verbose_name = 'child topic'


class TopicAdmin(Admin):
    """TODO: add docstring."""

    list_display = [
        'key',
        'detail_link',
        'description',
        'parent_topics_string',
        'child_topics_string',
        'tags_string'
    ]
    list_filter = ['related_topics']
    search_fields = ['key', 'aliases', 'description']
    ordering = ['key']

    inlines = [
        ParentTopicsInline,
        ChildTopicsInline,
        TopicRelationsInline,
        # RelatedOccurrencesInline,
    ]


admin_site.register(models.Topic, TopicAdmin)
