"""Model classes for facts."""

from django.db.models import CASCADE, ForeignKey, ManyToManyField

from history.fields import HTMLField
from history.models import Model
from topics.models.topics import Topic


class FactRelation(Model):
    """TODO: add docstring."""

    class Meta:
        abstract = True


class EntityFactRelation(FactRelation):
    """Relation of a fact to an entity."""
    entity = ForeignKey('entities.Entity', related_name='entity_fact_relations', on_delete=CASCADE)
    fact = ForeignKey('Fact', related_name='fact_entity_relations', on_delete=CASCADE)

    class Meta:
        unique_together = ['fact', 'entity']


class TopicFactRelation(FactRelation):
    """A relation of a fact to a topic."""

    topic = ForeignKey(Topic, related_name='topic_fact_relations', on_delete=CASCADE)
    fact = ForeignKey('Fact', related_name='fact_topic_relations', on_delete=CASCADE)

    class Meta:
        unique_together = ['topic', 'fact']


class OccurrenceFactRelation(FactRelation):
    """A relation of a fact to an occurrence."""

    occurrence = ForeignKey('occurrences.Occurrence', related_name='occurrence_fact_relations', on_delete=CASCADE)
    fact = ForeignKey('Fact', related_name='fact_occurrence_relations', on_delete=CASCADE)

    class Meta:
        unique_together = ['fact', 'occurrence']


class FactSupport(FactRelation):
    """TODO: add docstring."""

    supported_fact = ForeignKey('Fact', on_delete=CASCADE, related_name='supported_fact_supports')
    supportive_fact = ForeignKey('Fact', on_delete=CASCADE, related_name='supportive_fact_supports')

    class Meta:
        unique_together = ['supported_fact', 'supportive_fact']


class Fact(Model):
    """TODO: add docstring."""

    text = HTMLField(unique=True)
    supportive_facts = ManyToManyField(
        'self',
        through=FactSupport,
        related_name='supported_facts',
        symmetrical=False
    )
    related_entities = ManyToManyField(
        'entities.Entity',
        through=EntityFactRelation,
        related_name='facts'
    )
    related_topics = ManyToManyField(
        'topics.Topic',
        through=TopicFactRelation,
        related_name='facts'
    )
    related_occurrences = ManyToManyField(
        'occurrences.Occurrence',
        through=OccurrenceFactRelation,
        related_name='facts'
    )

    searchable_fields = ['text']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.text.text
