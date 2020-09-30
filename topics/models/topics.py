"""Model classes for topics."""

from django.db import models
from django.db.models import CASCADE, ForeignKey, ManyToManyField
from gm2m import GM2MField as GenericManyToManyField

from modularhistory.fields import ArrayField, HTMLField
from modularhistory.models import Model, ModelWithRelatedQuotes

KEY_MAX_LENGTH: int = 25


class TopicTopicRelation(Model):
    """A relationship between equivalent or closely related topics."""

    from_topic = ForeignKey('Topic', related_name='topics_related_to', on_delete=CASCADE)
    to_topic = ForeignKey('Topic', related_name='topics_related_from', on_delete=CASCADE)
    # relation_type = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ['from_topic', 'to_topic']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return f'{self.from_topic} ~ {self.to_topic}'


class TopicParentChildRelation(Model):
    """A relationship between a parent topic and child topic."""

    parent_topic = ForeignKey('Topic', related_name='child_relations', on_delete=CASCADE)
    child_topic = ForeignKey('Topic', related_name='parent_relations', on_delete=CASCADE)
    # relation_type = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ['parent_topic', 'child_topic']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return f'{self.parent_topic} > {self.child_topic}'


class Topic(ModelWithRelatedQuotes):
    """A topic."""

    key = models.CharField(max_length=KEY_MAX_LENGTH, unique=True)
    aliases = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    parent_topics = ManyToManyField(
        'self',
        through=TopicParentChildRelation,
        through_fields=('child_topic', 'parent_topic'),
        symmetrical=False,
        related_name='child_topics',
        blank=True
    )
    related_topics = ManyToManyField(
        'self',
        through=TopicTopicRelation,
        symmetrical=True,
        related_name='topics_related',
        blank=True
    )
    related = GenericManyToManyField(
        'occurrences.Occurrence',
        'quotes.Quote',
        through='topics.TopicRelation',
        related_name='topic_relations',
        blank=True
    )

    searchable_fields = ['key', 'description', 'aliases']

    class Meta:
        ordering = ['key']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.key

    @property
    def child_topics_string(self) -> str:
        """TODO: write docstring."""
        return ', '.join([str(topic) for topic in self.child_topics.all()])

    @property
    def parent_topics_string(self) -> str:
        """TODO: write docstring."""
        return ', '.join([str(topic) for topic in self.parent_topics.all()])

    @property
    def tags_string(self) -> str:
        """TODO: write docstring."""
        return ', '.join([str(topic) for topic in self.related_topics.all()])
