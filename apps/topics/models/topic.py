"""Model classes for topics."""

from django.db import models
from django.db.models import CASCADE, ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _

from apps.topics.serializers import TopicSerializer
from apps.trees.models import TreeModel
from core.fields import ArrayField, HTMLField
from core.models.model import Model
from core.models.model_with_cache import ModelWithCache, store
from core.models.slugged_model import SluggedModel

NAME_MAX_LENGTH: int = 25
TOPIC_STRING_DELIMITER = ', '


class TopicTopicRelation(Model):
    """A relationship between equivalent or closely related topics."""

    from_topic = ForeignKey(
        to='topics.Topic', on_delete=CASCADE, related_name='topics_related_to'
    )
    to_topic = ForeignKey(
        to='topics.Topic', on_delete=CASCADE, related_name='topics_related_from'
    )

    class Meta:
        unique_together = ['from_topic', 'to_topic']

    def __str__(self) -> str:
        """Return the string representation of the relation."""
        return f'{self.from_topic} ~ {self.to_topic}'


class TopicParentChildRelation(Model):
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
        """TODO: write docstring."""
        return f'{self.parent_topic} > {self.child_topic}'


class Topic(TreeModel, SluggedModel, ModelWithCache):
    """A topic."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    aliases = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_('aliases'),
        null=True,
        blank=True,
    )
    description = HTMLField(null=True, blank=True, paragraphed=True)
    parent_topics = ManyToManyField(
        to='self',
        through=TopicParentChildRelation,
        through_fields=('child_topic', 'parent_topic'),
        symmetrical=False,
        related_name='child_topics',
        blank=True,
    )
    related_topics = ManyToManyField(
        to='self',
        through=TopicTopicRelation,
        symmetrical=True,
        related_name='topics_related',
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
    @store(attribute_name='child_topics_string')
    def child_topics_string(self) -> str:
        """Return a list of the topic's child topics as a string."""
        return TOPIC_STRING_DELIMITER.join(
            [str(topic) for topic in self.child_topics.all()]
        )

    @property  # type: ignore
    @store(attribute_name='parent_topics_string')
    def parent_topics_string(self) -> str:
        """Return a list of the topic's parent topics as a string."""
        return TOPIC_STRING_DELIMITER.join(
            [str(topic) for topic in self.parent_topics.all()]
        )

    @property  # type: ignore
    @store(attribute_name='related_topics_string')
    def tags_string(self) -> str:
        """Return a list of the topic's related topics as a string."""
        return TOPIC_STRING_DELIMITER.join(
            [str(topic) for topic in self.related_topics.all()]
        )
