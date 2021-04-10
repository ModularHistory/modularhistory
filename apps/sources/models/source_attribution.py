from django.db import models
from django.utils.translation import ugettext_lazy as _

from modularhistory.models.positioned_relation import PositionedRelation


class SourceAttribution(PositionedRelation):
    """An entity (e.g., a writer or organization) to which a source is attributed."""

    source = models.ForeignKey(
        to='sources.Source',
        on_delete=models.CASCADE,
        related_name='attributions',
        null=True,
        verbose_name=_('source'),
    )
    polymorphic_source = models.ForeignKey(
        to='sources.PolymorphicSource',
        on_delete=models.CASCADE,
        related_name='attributions',
        null=True,
        verbose_name=_('source'),
    )
    attributee = models.ForeignKey(
        to='entities.Entity',
        on_delete=models.CASCADE,
        related_name='source_attributions',
    )

    def __str__(self) -> str:
        """Return the string representation of the source attribution."""
        return self.attributee.unabbreviated_name or f'{self.attributee}'
