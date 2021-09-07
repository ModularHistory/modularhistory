"""Model classes for topics."""

from django.db import models
from django.db.models import CASCADE, ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _

from apps.topics.serializers import TopicSerializer
from apps.trees.models import TreeModel
from core.fields.array_field import ArrayField
from core.fields.html_field import HTMLField
from core.models.model_with_cache import store
from core.models.module import Module
from core.models.relations.moderated import ModeratedRelation

NAME_MAX_LENGTH: int = 25
TOPIC_STRING_DELIMITER = ', '


class TopicRelation(ModeratedRelation):
    """A relationship between equivalent or closely related topics."""

    topic = ForeignKey(
        to='topics.Topic',
        on_delete=CASCADE,
        related_name='topic_relations',
        verbose_name='topic',
    )
    related_topic = ForeignKey(
        to='topics.Topic',
        on_delete=CASCADE,
        verbose_name='related topic',
    )

    class Meta:
        unique_together = ['topic', 'related_topic']

    def __str__(self) -> str:
        """Return the string representation of the relation."""
        return f'{self.topic} ~ {self.related_topic}'


class TopicParentChildRelation(ModeratedRelation):
    """A relationship between a parent topic and child topic."""

    parent_topic = ForeignKey(
        to='topics.Topic', on_delete=CASCADE, related_name='child_relations'
    )
    child_topic = ForeignKey(
        to='topics.Topic', on_delete=CASCADE, related_name='parent_relations'
    )

    class Meta:
        unique_together = ['parent_topic', 'child_topic']

    def __str__(self) -> str:
        return f'{self.parent_topic} > {self.child_topic}'


class Topic(TreeModel, Module):
    """A topic."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    aliases = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_('aliases'),
        null=True,
        blank=True,
    )
    description = HTMLField(
        blank=True,
        paragraphed=True,
    )
    related_topics = ManyToManyField(
        to='self',
        through=TopicRelation,
        symmetrical=True,
        related_name='related_topics',
        blank=True,
    )

    searchable_fields = [
        'name',
        # 'aliases',
        # 'description'
    ]
    serializer = TopicSerializer
    slug_base_fields = ('name',)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        """Return the topic's string representation."""
        return self.name

    @property  # type: ignore
    @store(attribute_name='related_topics_string')
    def tags_string(self) -> str:
        """Return a list of the topic's related topics as a string."""
        return TOPIC_STRING_DELIMITER.join(
            [str(topic) for topic in self.related_topics.all()]
        )

    def get_default_title(self) -> str:
        """Return the value the title should be set to, if not manually set."""
        return self.name
