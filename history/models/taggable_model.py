"""Taggable models."""

import re
from typing import List, Optional

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import reverse
from django.utils.html import SafeString, format_html

from history.models import Model
from topics.models import Topic


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""
    tags = GenericRelation('topics.TopicRelation')

    class Meta:
        abstract = True

    @property
    def has_tags(self) -> bool:
        """TODO: write docstring."""
        return bool(self.related_topics)

    @property
    def related_topics(self) -> List['Topic']:
        """TODO: write docstring."""
        if not self.tags.exists():
            return []
        return [tag.topic for tag in self.tags.all()]

    @property
    def tags_string(self) -> Optional[str]:
        """TODO: write docstring."""
        if self.has_tags:
            related_topics = [topic.key for topic in self.related_topics]
            if related_topics:
                return ', '.join(related_topics)
        return None

    @property
    def tags_html(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        if self.has_tags:
            return format_html(
                ' '.join([
                    f'<li class="topic-tag"><a>{topic.key}</a></li>'
                    for topic in self.related_topics
                ])
            )
        return None


class TopicFilter(AutocompleteFilter):
    """TODO: add docstring."""

    title = 'tags'
    field_name = 'tags'

    _parameter_name = 'tags__topic__pk__exact'

    def __init__(self, request, params, model, model_admin):
        """TODO: add docstring."""
        super().__init__(request, params, model, model_admin)
        rendered_widget: SafeString = self.rendered_widget  # type: ignore
        if self.value():
            topic = Topic.objects.get(pk=self.value())
            rendered_widget = format_html(
                re.sub(
                    r'(selected>).+(</option>)',
                    rf'\g<1>{topic}\g<2>',
                    rendered_widget
                )
            )
        self.rendered_widget = rendered_widget

    def get_autocomplete_url(self, request, model_admin):
        """TODO: add docstring."""
        return reverse('admin:tag_search')

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value():
            return queryset.filter(**{self._parameter_name: self.value()})
        return queryset
