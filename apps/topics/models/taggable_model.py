"""Taggable models."""

from typing import List, Optional

from celery import shared_task
from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.topics.models.topic import Topic
from core.fields.json_field import JSONField
from core.models.model_with_computations import ModelWithComputations


class TaggableModel(ModelWithComputations):
    """Mixin for models that are topic-taggable."""

    tags = GenericRelation('topics.TopicRelation')
    new_tags = models.ManyToManyField(
        to='topics.Topic',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('tags'),
    )
    _cached_tags = JSONField(editable=False, default=list)

    class Meta:
        abstract = True

    @property
    def cached_tags(self) -> list:
        if self._cached_tags or not self.new_tags.exists():
            return self._cached_tags
        tags = [tag.serialize() for tag in self.new_tags.all()]
        cache_tags.delay(
            f'{self.__class__._meta.app_label}.{self.__class__.__name__.lower()}',
            self.id,
            tags,
        )
        return tags

    @property  # type: ignore
    def tag_keys(self) -> Optional[List[str]]:
        """Return a list of tag keys (e.g., ['race', 'religion'])."""
        try:
            return [topic.name for topic in self.cached_tags]
        except Exception:
            return [topic['name'] for topic in self.cached_tags]

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
        # if self.cached_tags:
        #     return self.cached_tags
        try:
            tags = [tag.serialize() for tag in self.new_tags.all()]
            if tags:
                self.cached_tags = tags
                self.save()
            return tags
        except (AttributeError, ObjectDoesNotExist):
            return []


class TopicFilter(ManyToManyAutocompleteFilter):
    """Reusable filter for models with topic tags."""

    title = 'tags'
    field_name = 'tags'
    _parameter_name = 'new_tags__pk__exact'
    m2m_cls = Topic

    def get_autocomplete_url(self, request, model_admin):
        """Return the URL used for topic autocompletion."""
        return reverse('admin:tag_search')


@shared_task
def cache_tags(model: str, instance_id: int, tags: list):
    """Save cached tags to a model instance."""
    if not tags:
        return
    Model = apps.get_model(model)
    model_instance = Model.objects.get(pk=instance_id)
    model_instance._cached_tags = tags
    model_instance.save()
