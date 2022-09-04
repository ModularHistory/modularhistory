import logging
from typing import TYPE_CHECKING, Optional, Union

from django.apps import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.celery import app
from core.fields.custom_m2m_field import CustomManyToManyField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.relations.moderated import ModeratedRelation
from core.utils.sync import delay

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from core.models.model_with_cache import ModelWithCache


class AbstractTopicRelation(ModeratedRelation):
    """
    Abstract base model for topic relations.

    Models governing m2m relationships between `Topic` and another model
    should inherit from this abstract model.
    """

    topic = ManyToManyForeignKey(
        to='topics.Topic',
        related_name='%(app_label)s_%(class)s_set',
    )

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.topic.name}'

    def content_object(self) -> models.ForeignKey:
        """Foreign key to the model that references the topic."""
        raise NotImplementedError


class TagsField(CustomManyToManyField):
    """Custom field for related topics."""

    target_model = 'topics.Topic'
    through_model_base = AbstractTopicRelation

    def __init__(self, through: Union[type[AbstractTopicRelation], str], **kwargs):
        """Construct the field."""
        kwargs['through'] = through
        kwargs['verbose_name'] = _('tags')
        super().__init__(**kwargs)


class TaggableModel(models.Model):
    """Base model for models of which instances are topic-taggable."""

    class Meta:
        abstract = True

    @property
    def tags(self) -> TagsField:
        """
        Require implementation of a `tags` field on inheriting models.

        For example:
        ``
        tags = TagsField(through=TopicRelation)
        ``
        """
        raise NotImplementedError

    @property
    def topic_relations(self) -> 'QuerySet[AbstractTopicRelation]':
        """
        Require the intermediate model to specify `related_name='topic_relations'`.

        For example:
        ``
        class TopicRelation(AbstractTopicRelation):
            content_object = ManyToManyForeignKey(
                to='propositions.Proposition',
                related_name='topic_relations',
            )
        ``
        """

    @property
    def cached_tags(self: Union['TaggableModel', 'ModelWithCache']) -> list:
        """Return the model instance's cached tags."""
        cache: dict = getattr(self, 'cache', None) or {}
        tags = cache.get('tags', [])
        if tags or not self.tags.exists():
            return tags
        tags = [relation.topic.serialize() for relation in self.topic_relations.all()]
        delay(
            cache_tags,
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
    def tags_html(self) -> str:
        """Return the model instance's tags as an HTML string of <li> elements."""
        tags_html = ''
        if self.tag_keys:
            tags_html = ' '.join(
                [f'<li class="topic-tag"><a>{tag_key}</a></li>' for tag_key in self.tag_keys]
            )
        return tags_html


@app.task
def cache_tags(model: str, instance_id: int, tags: list):
    """Save cached tags to a model instance."""
    if not tags:
        return

    Model = apps.get_model(model)  # noqa: N806
    if not hasattr(Model, 'cache'):
        logging.error(f'{Model} has no cache.')
        return
    model_instance: 'ModelWithCache' = Model.objects.get(pk=instance_id)
    model_instance.cache['tags'] = tags
    model_instance.save(wipe_cache=False, moderate=False)
    model_instance.refresh_from_db()
