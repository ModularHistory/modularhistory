"""Model classes for postulations."""

from django.db import models

from modularhistory.models import Model
from topics.models.topic import Topic


class FactRelation(Model):
    """A relation of a fact to some other model."""

    class Meta:
        abstract = True


class EntityFactRelation(FactRelation):
    """Relation of a fact to an entity."""

    entity = models.ForeignKey(
        'entities.Entity',
        related_name='entity_fact_relations',
        on_delete=models.CASCADE,
    )
    fact = models.ForeignKey(
        'postulations.Postulation',
        related_name='fact_entity_relations',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ['fact', 'entity']


class TopicFactRelation(FactRelation):
    """A relation of a fact to a topic."""

    topic = models.ForeignKey(
        Topic, related_name='topic_fact_relations', on_delete=models.CASCADE
    )
    fact = models.ForeignKey(
        'postulations.Postulation',
        related_name='fact_topic_relations',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ['topic', 'fact']


class OccurrenceFactRelation(FactRelation):
    """A relation of a fact to an occurrence."""

    occurrence = models.ForeignKey(
        'occurrences.Occurrence',
        related_name='occurrence_fact_relations',
        on_delete=models.CASCADE,
    )
    fact = models.ForeignKey(
        'postulations.Postulation',
        related_name='fact_occurrence_relations',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ['fact', 'occurrence']
