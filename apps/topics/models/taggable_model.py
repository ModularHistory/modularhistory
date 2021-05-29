"""Taggable models."""

from typing import Optional

from celery import shared_task
from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.topics.models.topic import Topic
from core.models.model_with_cache import ModelWithCache
from core.models.slugged_model import SluggedModel


class TaggableModel(SluggedModel, ModelWithCache):
    """Mixin for models that are topic-taggable."""

    tags = models.ManyToManyField(
        to='topics.Topic',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('tags'),
    )

    class Meta:
        abstract = True

    @property
    def cached_tags(self) -> list:
        """Return the model instance's cached tags."""
        tags = self.cache.get('tags', [])
        if tags or not self.tags.exists():
            return tags
        tags = [tag.serialize() for tag in self.tags.all()]
        cache_tags.delay(
            f'{self.__class__._meta.app_label}.{self.__class__.__name__.lower()}',
            self.id,
            tags,
        )
        return tags

    @property  # type: ignore
    def tag_keys(self) -> Optional[list[str]]:
        """Return a list of tag keys (e.g., ['race', 'religion'])."""
        return [topic['name'] for topic in self.cached_tags]

    @property
    def tags_string(self) -> str:
        """Return a comma-delimited list of tags as a string."""
        if self.tag_keys:
            return ', '.join(self.tag_keys)
        return ''

    @property
    def tags_html(self) -> SafeString:
        """Return the model instance's tags as an HTML string of <li> elements."""
        tags_html = ''
        if self.tag_keys:
            tags_html = ' '.join(
                [
                    f'<li class="topic-tag"><a>{tag_key}</a></li>'
                    for tag_key in self.tag_keys
                ]
            )
        return format_html(tags_html)


class TopicFilter(ManyToManyAutocompleteFilter):
    """Reusable filter for models with topic tags."""

    title = 'tags'
    field_name = 'tags'
    _parameter_name = 'tags__pk__exact'
    m2m_cls = Topic

    def get_autocomplete_url(self, request, model_admin):
        """Return the URL used for topic autocompletion."""
        return reverse('admin:tag_search')


@shared_task
def cache_tags(model: str, instance_id: int, tags: list):
    """Save cached tags to a model instance."""
    if not tags:
        return
    Model = apps.get_model(model)  # noqa: N806
    model_instance: TaggableModel = Model.objects.get(pk=instance_id)
    model_instance.cache['tags'] = tags
    model_instance.save(wipe_cache=False)
    model_instance.refresh_from_db()
