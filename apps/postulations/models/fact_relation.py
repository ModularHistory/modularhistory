"""Model classes for postulations."""

from django.db import models

from apps.topics.models.topic import Topic
from core.models import Model


class FactRelation(Model):
    """A relation of a fact to some other model."""

    class Meta:
        """Meta options for FactRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True


class EntityFactRelation(FactRelation):
    """Relation of a fact to an entity."""

    entity = models.ForeignKey(
        to='entities.Entity',
        related_name='entity_fact_relations',
        on_delete=models.CASCADE,
    )
    fact = models.ForeignKey(
        to='postulations.Postulation',
        related_name='fact_entity_relations',
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta options for EntityFactRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together = ['fact', 'entity']


class TopicFactRelation(FactRelation):
    """A relation of a fact to a topic."""

    topic = models.ForeignKey(
        to=Topic, related_name='topic_fact_relations', on_delete=models.CASCADE
    )
    fact = models.ForeignKey(
        to='postulations.Postulation',
        related_name='fact_topic_relations',
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta options for TopicFactRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together = ['topic', 'fact']


class OccurrenceFactRelation(FactRelation):
    """A relation of a fact to an occurrence."""

    occurrence = models.ForeignKey(
        to='occurrences.Occurrence',
        related_name='occurrence_fact_relations',
        on_delete=models.CASCADE,
    )
    fact = models.ForeignKey(
        to='postulations.Postulation',
        related_name='fact_occurrence_relations',
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta options for OccurrenceFactRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together = ['fact', 'occurrence']
