"""Model classes for facts."""

from django.db.models import CASCADE, ForeignKey, ManyToManyField

from modularhistory.fields import HTMLField
from modularhistory.models import Model
from topics.models.fact_relations import (
    EntityFactRelation,
    FactRelation,
    OccurrenceFactRelation,
    TopicFactRelation,
)
from topics.serializers import FactSerializer


class FactSupport(FactRelation):
    """TODO: add docstring."""

    supported_fact = ForeignKey(
        'topics.Fact', on_delete=CASCADE, related_name='supported_fact_supports'
    )
    supportive_fact = ForeignKey(
        'topics.Fact', on_delete=CASCADE, related_name='supportive_fact_supports'
    )

    class Meta:
        unique_together = ['supported_fact', 'supportive_fact']

    serializer = FactSerializer


class Fact(Model):
    """A fact."""

    text = HTMLField(unique=True)
    elaboration = HTMLField(null=True, blank=True)
    supportive_facts = ManyToManyField(
        'self', through=FactSupport, related_name='supported_facts', symmetrical=False
    )
    related_entities = ManyToManyField(
        'entities.Entity', through=EntityFactRelation, related_name='facts'
    )
    related_topics = ManyToManyField(
        'topics.Topic', through=TopicFactRelation, related_name='facts'
    )
    related_occurrences = ManyToManyField(
        'occurrences.Occurrence', through=OccurrenceFactRelation, related_name='facts'
    )

    searchable_fields = ['text']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.text.text
