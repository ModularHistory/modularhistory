"""Model classes for ideas."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from modularhistory.fields import HTMLField
from modularhistory.models import Model

NAME_MAX_LENGTH: int = 100


class Idea(Model):
    """An idea."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = HTMLField(null=True, blank=True, paragraphed=True)
    promoters = models.ManyToManyField(
        to='entities.Entity', related_name='ideas', blank=True
    )

    class Meta:
        """Meta options for the Idea model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name = _('idea')

    def __str__(self):
        """Return the idea's string representation."""
        return self.name


class EntityIdea(Model):
    """An association or attribution of an idea to an entity."""

    entity = models.ForeignKey(
        to='entities.Entity',
        on_delete=models.CASCADE,
        related_name='entity_ideas',
        verbose_name=_('entity'),
    )
    idea = models.ForeignKey(
        to='entities.Idea',
        on_delete=models.CASCADE,
        related_name='entity_ideas',
        verbose_name=_('idea'),
    )

    class Meta:
        """Meta options for the EntityIdea model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        unique_together = ['entity', 'idea']
        verbose_name = _('entity idea')

    def __str__(self):
        """Return the string representation of the entity–idea association."""
        return f'{self.entity} : {self.idea}'
