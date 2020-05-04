import re
from typing import List, Optional, TYPE_CHECKING

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import reverse
from django.utils.safestring import mark_safe, SafeText

from topics.models import Topic
from .model import Model

if TYPE_CHECKING:
    from topics.models import Topic


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""
    tags = GenericRelation('topics.TopicRelation')

    class Meta:
        abstract = True

    @property
    def has_tags(self) -> bool:
        return bool(self.related_topics)

    @property
    def related_topics(self) -> List['Topic']:
        if not self.tags.exists():
            return []
        related_topics = [tag.topic for tag in self.tags.all()]
        return related_topics

    @property
    def tags_string(self) -> Optional[str]:
        if self.has_tags:
            related_topics = [topic.key for topic in self.related_topics]
            if related_topics:
                return ', '.join(related_topics)
        return None

    @property
    def tags_html(self) -> Optional[SafeText]:
        if self.has_tags:
            return mark_safe(
                ' '.join([
                    f'<li class="topic-tag"><a>{topic.key}</a></li>'
                    for topic in self.related_topics
                ])
            )
        return None


class TopicFilter(AutocompleteFilter):
    title = 'tags'
    field_name = 'tags'

    PARAMETER_NAME = 'tags__topic__pk__exact'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        rendered_widget = self.rendered_widget
        if self.value():
            topic = Topic.objects.get(pk=self.value())
            rendered_widget = mark_safe(
                re.sub(r'(selected>).+(</option>)',
                       rf'\g<1>{topic}\g<2>',
                       rendered_widget)
            )
        self.rendered_widget = rendered_widget

    def get_autocomplete_url(self, request, model_admin):
        return reverse('admin:tag_search')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.PARAMETER_NAME: self.value()})
        else:
            return queryset
