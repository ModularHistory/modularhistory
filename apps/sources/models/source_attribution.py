from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.relations.moderated import ModeratedPositionedRelation

if TYPE_CHECKING:
    from apps.entities.models import Entity


class SourceAttribution(ModeratedPositionedRelation):
    """An attribution of a source to an entity (e.g., a writer or organization)."""

    source = models.ForeignKey(
        to='sources.Source',
        on_delete=models.CASCADE,
        related_name='attributions',
        verbose_name=_('source'),
    )
    attributee = models.ForeignKey(
        to='entities.Entity',
        on_delete=models.CASCADE,
        related_name='source_attributions',
    )

    def __str__(self) -> str:
        """Return the string representation of the source attribution."""
        attributee: 'Entity' = self.attributee
        return attributee.unabbreviated_name or f'{attributee}'
