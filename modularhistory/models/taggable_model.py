"""Taggable models."""

from typing import List, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.utils.html import SafeString, format_html

from admin.autocomplete_filter import ManyToManyAutocompleteFilter
from modularhistory.models.model_with_computations import ModelWithComputations
from topics.models import Topic


class TaggableModel(ModelWithComputations):
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
        try:
            tags = self.tags.select_related('topic')
            return [tag.topic for tag in tags]
        except (AttributeError, ObjectDoesNotExist) as e:
            return []

    @property
    def tag_keys(self) -> Optional[List[str]]:
        tag_keys = self.computations.get('tag_keys')
        if not tag_keys:
            tag_keys = [topic.key for topic in self.related_topics]
            # TODO: update asynchronously
            self.computations['tag_keys'] = tag_keys
            self.save()
        return tag_keys

    @property
    def tags_string(self) -> Optional[str]:
        """TODO: write docstring."""
        if self.has_tags:
            return ', '.join(self.tag_keys)
        return None

    @property
    def tags_html(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        if self.has_tags:
            return format_html(
                ' '.join([
                    f'<li class="topic-tag"><a>{tag_key}</a></li>'
                    for tag_key in self.tag_keys
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
