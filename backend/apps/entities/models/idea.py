"""Model classes for ideas."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.html_field import HTMLField
from core.models.model import ExtendedModel

NAME_MAX_LENGTH: int = 100


class Idea(ExtendedModel):
    """An idea."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = HTMLField(blank=True, paragraphed=True)
    promoters = models.ManyToManyField(to='entities.Entity', related_name='ideas', blank=True)

    class Meta:
        """Meta options for the Idea model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name = _('idea')

    def __str__(self) -> str:
        """Return the idea's string representation."""
        return self.name


class EntityIdea(ExtendedModel):
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

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        unique_together = ['entity', 'idea']
        verbose_name = _('entity idea')

    def __str__(self) -> str:
        """Return the string representation of the entity–idea association."""
        return f'{self.entity} : {self.idea}'
