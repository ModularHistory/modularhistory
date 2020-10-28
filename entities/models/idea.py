"""Model classes for ideas."""

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE

from modularhistory.fields import HTMLField
from modularhistory.models import Model

NAME_MAX_LENGTH: int = 100


class Idea(Model):
    """TODO: add docstring."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = HTMLField(null=True, blank=True)
    promoters = ManyToManyField('entities.Entity', related_name='ideas', blank=True)

    def __str__(self):
        """Return the idea's string representation."""
        return self.name


class EntityIdea(Model):
    """An association or attribution of an idea to an entity."""

    entity = ForeignKey(
        'entities.Entity', on_delete=CASCADE, related_name='entity_ideas'
    )
    idea = ForeignKey('entities.Idea', on_delete=CASCADE, related_name='entity_ideas')

    class Meta:
        unique_together = ['entity', 'idea']

    def __str__(self):
        """Return the string representation of the entity–idea association."""
        return f'{self.entity} : {self.idea}'
