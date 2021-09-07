from apps.admin import TabularInline
from apps.topics import models


class TopicRelationsInline(TabularInline):
    """Inline admin for a topic's related topics."""

    model = models.Topic.related_topics.through
    fk_name = 'topic'
    autocomplete_fields = ['related_topic']
    extra = 1
    verbose_name_plural = 'related topics'
    verbose_name = 'related topic'
