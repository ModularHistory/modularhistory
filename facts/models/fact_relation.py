"""Model classes for facts."""

from django.db.models import CASCADE, ForeignKey

from modularhistory.models import Model
from topics.models.topics import Topic


class FactRelation(Model):
    """A relation of a fact to some other model."""

    class Meta:
        abstract = True


class EntityFactRelation(FactRelation):
    """Relation of a fact to an entity."""

    entity = ForeignKey(
        'entities.Entity', related_name='entity_fact_relations', on_delete=CASCADE
    )
    fact = ForeignKey(
        'facts.Fact', related_name='fact_entity_relations', on_delete=CASCADE
    )

    class Meta:
        unique_together = ['fact', 'entity']


class TopicFactRelation(FactRelation):
    """A relation of a fact to a topic."""

    topic = ForeignKey(Topic, related_name='topic_fact_relations', on_delete=CASCADE)
    fact = ForeignKey(
        'facts.Fact', related_name='fact_topic_relations', on_delete=CASCADE
    )

    class Meta:
        unique_together = ['topic', 'fact']


class OccurrenceFactRelation(FactRelation):
    """A relation of a fact to an occurrence."""

    occurrence = ForeignKey(
        'occurrences.Occurrence',
        related_name='occurrence_fact_relations',
        on_delete=CASCADE,
    )
    fact = ForeignKey(
        'facts.Fact', related_name='fact_occurrence_relations', on_delete=CASCADE
    )

    class Meta:
        unique_together = ['fact', 'occurrence']
