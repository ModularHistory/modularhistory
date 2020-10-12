"""Taggable models."""

from typing import List, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import reverse
from django.utils.html import SafeString, format_html

from admin.autocomplete_filter import ManyToManyAutocompleteFilter
from modularhistory.models import Model
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


class TopicFilter(ManyToManyAutocompleteFilter):
    """TODO: add docstring."""

    title = 'tags'
    field_name = 'tags'

    _parameter_name = 'tags__topic__pk__exact'
    m2m_cls = Topic

    def get_autocomplete_url(self, request, model_admin):
        """TODO: add docstring."""
        return reverse('admin:tag_search')
