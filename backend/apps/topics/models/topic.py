"""Model classes for topics."""

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import CASCADE, ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import Serializer

from apps.topologies.models import edge_factory, node_factory
from core.fields.array_field import ArrayField
from core.fields.html_field import HTMLField
from core.models.model_with_cache import store
from core.models.module import Module
from core.models.relations.moderated import ModeratedRelation

if TYPE_CHECKING:
    from apps.topologies.models.dag import Node as BaseNode


NAME_MAX_LENGTH: int = 25
TOPIC_STRING_DELIMITER = ', '


Edge = edge_factory(node_model='topics.Topic', bases=(ModeratedRelation,))


class TopicEdge(Edge):
    """An edge in the directed acyclic graph of topics."""


class TopicRelation(ModeratedRelation):
    """A non-topological relationship between closely related topics."""

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


Node: type['BaseNode'] = node_factory(edge_model=TopicEdge)


class Topic(Node, Module):
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
    slug_base_fields = ('name',)

    class Meta:
        ordering = ['name']

    @classmethod
    def get_serializer(self) -> Serializer:
        """Return the serializer for the entity."""
        from apps.topics.api.serializers import TopicSerializer

        return TopicSerializer

    def __str__(self) -> str:
        """Return the topic's string representation."""
        return self.name

    def pre_save(self):
        Node.pre_save(self)
        Module.pre_save(self)

    def post_save(self):
        Node.post_save(self)
        Module.post_save(self)

    @property  # type: ignore
    @store(key='related_topics_string')
    def tags_string(self) -> str:
        """Return a list of the topic's related topics as a string."""
        return TOPIC_STRING_DELIMITER.join(
            [str(topic) for topic in self.related_topics.all()]
        )

    def get_default_title(self) -> str:
        """Return the value the title should be set to, if not manually set."""
        return self.name
