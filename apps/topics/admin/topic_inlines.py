from admin import TabularInline
from apps.topics import models


class TopicRelationsInline(TabularInline):
    """Inline admin for a topic's related topics."""

    model = models.Topic.related_topics.through
    fk_name = 'from_topic'
    autocomplete_fields = ['to_topic']
    extra = 1
    verbose_name_plural = 'related topics'
    verbose_name = 'related topic'


class ParentTopicsInline(TabularInline):
    """Inline admin for a topic's parent topics."""

    model = models.Topic.parent_topics.through
    fk_name = 'child_topic'
    autocomplete_fields = ['parent_topic']
    extra = 1
    verbose_name_plural = 'parent topics'
    verbose_name = 'parent topic'


class ChildTopicsInline(TabularInline):
    """Inline admin for a topic's child topics."""

    model = models.Topic.parent_topics.through
    fk_name = 'parent_topic'
    autocomplete_fields = ['child_topic']
    extra = 1
    verbose_name_plural = 'child topics'
    verbose_name = 'child topic'
