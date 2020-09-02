# type: ignore
# TODO: remove above line after fixing typechecking

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE

from history.fields import HTMLField
from history.models import (
    Model
)


class Idea(Model):
    """TODO: add docstring."""

    NAME_MAX_LENGTH: int = 100

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = HTMLField(null=True, blank=True)
    promoters = ManyToManyField('entities.Entity', related_name='ideas', blank=True)
    # related_ideas = ManyToManyField('self', )


class EntityIdea(Model):
    """TODO: add docstring."""

    entity = ForeignKey('entities.Entity', on_delete=CASCADE, related_name='entity_ideas')
    idea = ForeignKey(Idea, on_delete=CASCADE, related_name='entity_ideas')

    class Meta:
        unique_together = ['entity', 'idea']
