"""Taggable models."""

from typing import List, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.topics.models import Topic
from core.models.model import Model
from core.models.model_with_computations import retrieve_or_compute


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""

    tags = GenericRelation('topics.TopicRelation')

    class FieldNames(Model.FieldNames):
        tags = 'tags'

    class Meta:
        abstract = True

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='tag_keys')
    def tag_keys(self) -> Optional[List[str]]:
        """Return a list of tag keys (e.g., ['race', 'religion'])."""
        return [topic.key for topic in self._related_topics]

    @property
    def tags_string(self) -> Optional[str]:
        """Return a comma-delimited list of tags as a string."""
        if self.tag_keys:
            return ', '.join(self.tag_keys)
        return None

    @property
    def tags_html(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        if self.tag_keys:
            return format_html(
                ' '.join(
                    [
                        f'<li class="topic-tag"><a>{tag_key}</a></li>'
                        for tag_key in self.tag_keys
                    ]
                )
            )
        return None

    @property
    def _related_topics(self) -> List['Topic']:
        """
        Return a list of topics related to the model instance.

        WARNING: This executes a db query for each model instance that accesses it.
        """
        try:
            tags = self.tags.select_related('topic')
            return [tag.topic for tag in tags]
        except (AttributeError, ObjectDoesNotExist):
            return []


class TopicFilter(ManyToManyAutocompleteFilter):
    """TODO: add docstring."""

    title = 'tags'
    field_name = 'tags'
    _parameter_name = 'tags__topic__pk__exact'
    m2m_cls = Topic

    def get_autocomplete_url(self, request, model_admin):
        """TODO: add docstring."""
        return reverse('admin:tag_search')
